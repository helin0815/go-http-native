package httpd

import (
	"fmt"
	"net"
)

type Handler interface {
	ServerHttp(w ResponseWriter, r *Request)
}

type Server struct {
	Addr    string
	Handler Handler
}

func (s *Server) ListenAndServe() error {

	l, err := net.Listen("tcp", s.Addr)
	if err != nil {
		fmt.Println("err happened:", err.Error())
		return err
	}
	for {
		rwc, err := l.Accept()
		if err != nil {
			continue
		}
		conn := newConn(rwc, s)
		go conn.serve()
	}
}
