I didn't write the whole code. 
Initial code was copied form: https://gist.github.com/n3wtron/4624820

This code was modified to stream everything that's a video resource. 
```
    arg should be:
        int for streaming cameras. Example 0, 1, 2
        url for RTSP video: example rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov
        filepath for video. example sample.mp4
```

# docker
To test, run the following command from project directory. 
docker build -t foo . && docker run -it -p 6420:6420 foo

