import http.server
import socketserver
from dashboard import dashboard

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Trigger the dashboard function to generate index.html
            dashboard()
            # Serve index.html as response
            with open('index.html', 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(file.read())
        else:
            # Serve other files (e.g., CSS, JS) as usual
            super().do_GET()


def main():
    PORT = 8000  # You can adjust the port as needed
    with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
        print("Server started at http://localhost:%s" % PORT)
        httpd.serve_forever()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
