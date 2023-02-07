package httpd

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"time"
)

type Helin struct {
	Name string `json:"name"`
}
type conn struct {
	svr  *Server
	rwc  net.Conn
	bufw *bufio.Writer
	lr   *io.LimitedReader
	bufr *bufio.Reader
	//hl   *Helin
}

func newConn(rwc net.Conn, svr *Server) *conn {
	lr := &io.LimitedReader{R: rwc, N: 1 << 20}
	return &conn{
		svr:  svr,
		rwc:  rwc,
		bufw: bufio.NewWriterSize(rwc, 4<<10),
		lr:   lr,
		bufr: bufio.NewReaderSize(lr, 4<<10),
	}
}

func (c *conn) serve() {
	defer func() {
		if err := recover(); err != nil {
			fmt.Println("panic recovered,err:", err)
		}
		c.close()
	}()
	fmt.Println("name is:", c.getName())
	for {
		time.Sleep(1 * time.Second)
		req, err := c.readRequest()
		if err != nil {
			handleErr(err, c)
			return
		}
		res := c.setupResponse()
		c.svr.Handler.ServerHttp(res, req)
		if err = c.bufw.Flush(); err != nil {
			return
		}
	}

}

func (c *conn) readRequest() (*Request, error) { return readRequest(c) }
func (c *conn) setupResponse() *response {
	return setupResponse(c)
}
func (c *conn) close()             { c.rwc.Close() }
func handleErr(err error, c *conn) { fmt.Println("err:", err.Error()) }
func (c *conn) getName() string {
	fmt.Println("helin name")
	return "helinnn"
}
