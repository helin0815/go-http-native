package main

import (
	"fmt"
	"strings"
)

type he map[string][]string

func main() {
	//url := "localhost:8080?name=helin&age=20&sex=male&love=woman"
	//data := parseQuery(url)
	//fmt.Println("data:", data)
	h := make(he)
	h["name"] = append(h["name"], "dsaa")
	fmt.Println("hh:", h)
}

func parseQuery(RawQuery string) map[string]string {
	parts := strings.Split(RawQuery, "&")
	fmt.Println("parts:", parts)
	queries := make(map[string]string, len(parts))
	fmt.Println("queries:", queries)
	for _, part := range parts {
		fmt.Println("part2:", part)
		index := strings.IndexByte(part, '=')
		fmt.Println("index:", index)
		fmt.Println("part[:index]", part[:index])
		if index == -1 || index == len(part)-1 {
			continue
		}
		queries[strings.TrimSpace(part[:index])] = strings.TrimSpace(part[index+1:])
	}
	return queries
}
