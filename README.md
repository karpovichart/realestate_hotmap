real estate price web visualisation
## Start app
1. `clone https://github.com/karpovichart/realestate_hotmap.git`
2. `cd realestate_hotmap`
3. `uv sync`
4. `uvicorn main:app --host 0.0.0.0 --port 8010`
5. Enter http://0.0.0.0:8010/get/?x=59.963966&y=30.302725
## In Docker
1. `clone https://github.com/karpovichart/realestate_hotmap.git`
2. `docker build . -t rs:v0.1` 
3. `docker run -it -p 8100:8100 rs:v0.1`
4. Enter http://0.0.0.0:8100/get/?x=59.963966&y=30.302725
