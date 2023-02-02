package main

import (
	"fmt"

	"helin.http.com/m/v2/http1"
)

func main() {
	wordStr := http1.ReturnHello()
	fmt.Println("hello", wordStr)
}
