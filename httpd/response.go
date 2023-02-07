package httpd

type response struct {
	c *conn
}

func setupResponse(c *conn) *response {
	return &response{c: c}
}

type ResponseWriter interface {
	Write([]byte) (n int, err error)
}

func (w *response) Write(p []byte) (int, error) {
	return w.c.bufw.Write(p)
}
