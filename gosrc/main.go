package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
)

var validID = regexp.MustCompile(`^\d+$`)

func transcriptsHandler(w http.ResponseWriter, r *http.Request) {
	path_args := strings.Split(r.URL.Path, "/")

	if len(path_args) < 3 {
		http.Error(w, "Bad path!", http.StatusBadRequest)
		return
	}

	userid := path_args[2]
	unix_timestamp := path_args[3]

	if !validID.MatchString(userid) || !validID.MatchString(unix_timestamp) {
		http.Error(w, "Invalid ID or timestamp format!", http.StatusBadRequest)
		return
	}

	tryPath := fmt.Sprintf("./transcripts/user-%s-%s.html", userid, unix_timestamp)
	if _, err := os.Stat(tryPath); os.IsNotExist(err) {
		http.NotFound(w, r)
		return
	}

	http.ServeFile(w, r, tryPath)
}

func main() {
	http.HandleFunc("/transcript/", transcriptsHandler)

	log.Fatal(http.ListenAndServe(":8069", nil))
}
