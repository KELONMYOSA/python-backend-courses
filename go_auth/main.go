package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	pb "go_auth/pb_auth"
	"go_auth/utils/auth"

	"google.golang.org/grpc"
)

var port = flag.Int("port", 50051, "port to run the server on")

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))

	if err != nil {
		log.Fatalln("Unable to start the server on port", *port)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterAuthServiceServer(grpcServer, &auth.Server{})
	log.Println("Started server at", lis.Addr())

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalln("Failed to start server at", lis.Addr())
	}
}
