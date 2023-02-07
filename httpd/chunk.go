package httpd

import (
	"bufio"
	"errors"
	"io"
)

type chunkReader struct {
	n    int
	bufr *bufio.Reader
	done bool
	crlf [2]byte
}

func (cw *chunkReader) Read(p []byte) (n int, err error) {
	if cw.done {
		return 0, err
	}
	if cw.n == 0 {
		cw.n, err = cw.getChunkSize()
		if err != nil {
			return
		}
	}
	if cw.n == 0 {
		cw.done = true
		err = cw.discardCRLF()
		return
	}
	if len(p) <= cw.n {
		n, err = cw.bufr.Read(p)
		cw.n = n
		return n, err
	}
	n, _ = io.ReadFull(cw.bufr, p[:cw.n])
	cw.n = 0
	if err = cw.discardCRLF(); err != nil {
		return
	}
	return
}
func (cw *chunkReader) getChunkSize() (chunkSize int, err error) {
	line, err := readLine(cw.bufr)
	if err != nil {
		return
	}
	for i := 0; i < len(line); i++ {
		switch {
		case 'a' <= line[i] && line[i] <= 'f':
			chunkSize = chunkSize*16 + int(line[i]-'a') + 10
		case 'A' <= line[i] && line[i] <= 'F':
			chunkSize = chunkSize*16 + int(line[i]-'A') + 10
		case '0' <= line[i] && line[i] <= '9':
			chunkSize = chunkSize*16 + int(line[i]-'0')
		default:
			return 0, errors.New("illegal hex number")
		}
	}
	return
}

func (cw *chunkReader) discardCRLF() (err error) {
	if _, err := io.ReadFull(cw.bufr, cw.crlf[:]); err != nil {
		return errors.New("unsupported encoding format of chunk")
	}
	return
}
