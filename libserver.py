import sys
import selectors
import json
import io
import struct

# library containing values of bridge game to get or set:
# valid actions:

valid_actions = ['get','card','stroke','contract','leader','player','claim','spel','laad','finishbid','nakaarten','nextgame','result','seed','bid','clear','undo','redo','check']
#  action buffers for the different hands:
north = {}
south = {}
west = {}
east = {}
playera = {}
playerm = {}


class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            #print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        action = self.request.get("action")
        value = self.request.get("value")
        player = self.request.get("player")
        if action == "get":
            if player == 'N':
                keys = list(north.keys())
                if len(keys) > 0:
                    val = north.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            elif player == 'O':
                keys = list(east.keys())
                if len(keys) > 0:
                    val = east.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            elif player == 'Z':
                keys = list(south.keys())
                if len(keys) > 0:
                    val = south.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            elif player == 'W':
                keys = list(west.keys())
                if len(keys) > 0:
                    val = west.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            elif player == 'M':
                keys = list(playerm.keys())
                if len(keys) > 0:
                    val = playerm.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            else: 
                keys = list(playera.keys())
                if len(keys) > 0:
                    val = playera.pop(keys[0])
                else:
                    keys = ['-']
                    val = '-'
            content = {"action": keys[0],"value":val}
        elif action == 'clear':   # clean up remaining stuff in the libraries:
             keys = list(playera.keys())
             for key in keys:
                 playera.popitem()
             keys = list(playerm.keys())
             for key in keys:
                 playerm.popitem()
             keys = list(north.keys())
             for key in keys:
                 north.popitem()
             keys = list(east.keys())
             for key in keys:
                 east.popitem()
             keys = list(south.keys())
             for key in keys:
                 south.popitem()
             keys = list(west.keys())
             for key in keys:
                 west.popitem()
             content = {"action": '-',"value":'-'}
        elif action == 'check':   # check the number of 
            value = 0
            if player != 'N': value += len(list(north.keys()))
            if player != 'O': value += len(list(east.keys()))
            if player != 'Z': value += len(list(south.keys()))
            if player != 'W': value += len(list(west.keys()))
            content = {"action":action, "value": value}
        elif valid_actions.count(action) == 1:
            # set value in database: e.g. bid 12 N means bid by north #12 
            if player != 'N': north[action] = value
            if player != 'O': east[action] = value
            if player != 'Z': south[action] = value
            if player != 'W': west[action] = value
            if player != 'A': playera[action] = value
            if player != 'M': playerm[action] = value
            content = {"action":action, "value": value}
        else:
            content = {"result": f'Error: invalid action "{action}".', "hands":hands}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        #print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        #print('len hrdlen',hdrlen)
        if len(self._recv_buffer) >= hdrlen:
            #print(self._recv_buffer[:hdrlen])
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            #print(self.jsonheader)
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            #print("received request", repr(self.request), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            #print(
            #    f'received {self.jsonheader["content-type"]} request from',
            #    self.addr,
            #)
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message
