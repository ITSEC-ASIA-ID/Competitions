# TimeOff
tl;dr

LFI from the file name parameter

### Solution

Participants are provided with a website built with ruby, participant also provided with the source code of the web

![image](https://github.com/user-attachments/assets/4c49d2a6-c519-44a7-b1fa-7948671cac59)

upon source code inspection, we found credentials on the `seeders.rb` file, we found 2 credentials, `admin@example.com:admin123` and `user@example.com:user123`

upon logging in we found that the `user` can request for a timeoff

![Image](https://github.com/user-attachments/assets/cdeb0bc1-22d4-49b0-bc37-25c05ae8cfd1)

after that we tried to upload a file from the timeoff request feature

![Image](https://github.com/user-attachments/assets/fdf554b5-cd02-47c9-a076-1edc4ed081f9)

then we try to open the file from that request

![Image](https://github.com/user-attachments/assets/09a21b35-82a9-4a04-a65a-908024bb5149)

notice that it says file not found on `/timeoff_app/public/uploads/test` even thought we sucessfully upload the file, maybe if we name file as a file that's already in the server we can open it in other word `LFI vulnerability`, so we try to find where is the location of flag.txt and from the Dockerfile we know that its on the `/timeoff_app/` folder

```
FROM ruby:3.2

RUN apt-get update -qq && apt-get install -y nodejs
RUN mkdir /timeoff_app
WORKDIR /timeoff_app

COPY app/Gemfile app/Gemfile.lock ./
RUN bundle install

COPY app/ ./
COPY flag.txt /timeoff_app/flag.txt

RUN mkdir -p tmp/pids

RUN rails assets:precompile

EXPOSE 3000
CMD ["bash", "-c", "bundle exec rake db:consolidate_and_seed && bundle exec puma -C config/puma.rb"]
```
so we just need to name our file `../../flag.txt` to go up by 2 levels and get the flag.txt

![Image](https://github.com/user-attachments/assets/869cbcdb-f302-4055-ba17-1475c1d25068)

then we can clink on the file name and download the flag.txt

![Image](https://github.com/user-attachments/assets/59b0f313-c9d2-4682-bdb6-214af987a097)

even thought the file name will be the same as the file we upload not the file name we provided, it will still contain the file based on the file name we provided which we can open using notepad

![Image](https://github.com/user-attachments/assets/5874b248-2771-4849-a8bc-5d1b9796d039)
