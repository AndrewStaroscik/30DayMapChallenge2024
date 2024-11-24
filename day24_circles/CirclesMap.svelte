<script>

  /* 
  This is a svelte component. 
  With proper access to the json files this can be built and used anywhere on the web
  */

  import { onMount } from "svelte";
  import * as d3 from 'd3';

  let canvas, ctx;
  let world;
  let pop;
  let area;
  const centerLong = -10;
  const centerLat = 10; 
  let projection; 

  let rotate = [-centerLong, -centerLat, 0];


  const drawCanvas = (width, height) => {
      
    projection = d3.geoOrthographic()
      .scale((385 * Math.min(width, height)) / 800)
      .translate([width / 2, height / 2])
      .clipAngle(90)
      .rotate(rotate);

      
    const path = d3.geoPath(projection, ctx);


    ctx.clearRect(0, 0, width, height);

    // base map
    ctx.beginPath();
    path(world);
    ctx.fillStyle = 'rgba(0, 34, 72, 1)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(0, 36, 77, 1)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // population circle
    ctx.beginPath();
    path(pop);
    ctx.strokeStyle = 'rgba(255, 219, 179, .8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // land area circle
    ctx.beginPath();
    path(area);
    ctx.fillStyle = 'rgba(249, 255, 93, 0.5)';
    ctx.fill();

    // add legend
    let x = 16 * Math.min(width, height) / 800
    let r = 15 * Math.min(width, height) / 800

    ctx.beginPath();
    ctx.arc(x, x, r, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(249, 255, 93, 0.5)';
    ctx.fill()  
    
    ctx.font = `${r}px Arial`
    ctx.fillStyle ='rgba(249, 255, 93, 0.9)';
    ctx.textBaseline = 'middle';
    ctx.fillText('Land Area', x*2.5, x);

    ctx.beginPath();
    ctx.arc(x, x*3.2, r, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(255, 219, 179, .8)';
    ctx.stroke();

    ctx.font = `${r}px Arial`
    ctx.fillStyle ='rgba(255, 219, 179, 1)';
    ctx.textBaseline = 'middle';
    ctx.fillText('Population', x*2.5, x*3.2);

  };

  const resizeCanvas = () => {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const size = Math.min(800, viewportWidth, viewportHeight); 

    canvas.width = size;
    canvas.height = size;

    drawCanvas(canvas.width, canvas.height);
  };


  const addDragBehavior = () => {
    let previousPosition = null;

    const drag = d3.drag()
      .on('start', (event) => {
        previousPosition = [event.x, event.y];
      })
      .on('drag', (event) => {
        if (!previousPosition) return;

        const [prevX, prevY] = previousPosition;
        const deltaX = event.x - prevX;
        const deltaY = event.y - prevY;


        const rotationDrag = 0.75;        
        rotate[0] += deltaX * rotationDrag;
        rotate[1] -= deltaY * rotationDrag;
        
        //uncomment to prevent rotation past the poles. 
        //rotate[1] = Math.max(-90, Math.min(90, rotate[1]));

        previousPosition = [event.x, event.y];

        
        drawCanvas(canvas.width, canvas.height);
      })
      .on('end', () => {
        previousPosition = null;
      });

    d3.select(canvas).call(drag);
  };

  onMount(async () => {
    canvas = document.querySelector('#mapCanvas');
    ctx = canvas.getContext('2d');

    const response = await fetch('./data/worldSm.geojson');
    world = await response.json();

    const response2 = await fetch('./data/countryPops.json');
    pop = await response2.json();

    const response3 = await fetch('./data/countryAreas.json');
    area = await response3.json();

    resizeCanvas();

    window.addEventListener('resize', resizeCanvas);
    addDragBehavior();
    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  });
</script>

👋🏻

<div id="map">
  <canvas id="mapCanvas"></canvas>
</div>
<div id='sig'><span style='font-size:1.2em; color:#9C9AE7;'>Andrew Staroscik</span><br /><span style='font-size:0.9em; color:#9C9AE7;'>#30DayMapChallenge</span></div>
<div id='minfo' style='font-size:0.8em; color:#9C9AE7;'><a href='https://github.com/AndrewStaroscik/30DayMapChallenge2024/tree/main/day24_circles'>More Information</a></div>

<style>
  #map {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
      width: 100%;
  }
  #sig {
    position: fixed;
    right: 10px;
    bottom: 10px;
  }
  #minfo {
    position: fixed;
    left: 10px;
    bottom: 10px;
  }

</style>