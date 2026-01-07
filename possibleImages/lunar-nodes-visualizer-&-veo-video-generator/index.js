import React, { useRef, useEffect, useState, useCallback } from 'react';
import ReactDOM from 'react-dom/client';
import * as d3 from 'd3';
import { GoogleGenAI } from "@google/genai";

// constants.ts
const VEO_MODEL_NAME = 'veo-3.1-fast-generate-preview';
const LUNAR_NODES_MODEL = 'gemini-3-flash-preview';
const SUN_RADIUS = 30;
const EARTH_ORBIT_RADIUS = 200;
const EARTH_RADIUS = 10;
const MOON_ORBIT_RADIUS = 40;
const MOON_RADIUS = 5;
const ORBIT_INCLINATION_ANGLE = 5.2 * (Math.PI / 180);
const EARTH_ORBITAL_PERIOD = 365 * 100;
const MOON_ORBITAL_PERIOD = 27 * 100;
const RAHU_ICON_PATH = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm-2 13.5l1-1 1 1V18h-2zM12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z";
const KETU_ICON_PATH = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm-2 13.5l1-1 1 1V18h-2zM12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z";
const ZODIAC_SIGNS = [
  { name: 'Aries', symbol: '♈', startAngle: 0 * (Math.PI / 6), startDate: 'Mar 21' },
  { name: 'Taurus', symbol: '♉', startAngle: 1 * (Math.PI / 6), startDate: 'Apr 20' },
  { name: 'Gemini', symbol: '♊', startAngle: 2 * (Math.PI / 6), startDate: 'May 21' },
  { name: 'Cancer', symbol: '♋', startAngle: 3 * (Math.PI / 6), startDate: 'Jun 21' },
  { name: 'Leo', symbol: '♌', startAngle: 4 * (Math.PI / 6), startDate: 'Jul 23' },
  { name: 'Virgo', symbol: '♍', startAngle: 5 * (Math.PI / 6), startDate: 'Aug 23' },
  { name: 'Libra', symbol: '♎', startAngle: 6 * (Math.PI / 6), startDate: 'Sep 23' },
  { name: 'Scorpio', symbol: '♏', startAngle: 7 * (Math.PI / 6), startDate: 'Oct 23' },
  { name: 'Sagittarius', symbol: '♐', startAngle: 8 * (Math.PI / 6), startDate: 'Nov 22' },
  { name: 'Capricorn', symbol: '♑', startAngle: 9 * (Math.PI / 6), startDate: 'Dec 22' },
  { name: 'Aquarius', symbol: '♒', startAngle: 10 * (Math.PI / 6), startDate: 'Jan 20' },
  { name: 'Pisces', symbol: '♓', startAngle: 11 * (Math.PI / 6), startDate: 'Feb 19' },
];
const ZODIAC_RADIUS_OFFSET = 30;
const ZODIAC_SYMBOL_FONT_SIZE = '20px';

// services/veoService.ts
async function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === 'string') {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      } else {
        reject(new Error('Failed to convert blob to base64.'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function encode(bytes) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function decode(base64) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

const generateVideo = async ({
  prompt,
  imageBase64,
  imageMimeType,
  aspectRatio,
}) => {
  try {
    // Always create a new GoogleGenAI instance right before an API call
    // to ensure it uses the most up-to-date API key from the dialog.
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

    let operation = await ai.models.generateVideos({
      model: VEO_MODEL_NAME,
      prompt: prompt,
      ...(imageBase64 && imageMimeType && {
        image: {
          imageBytes: imageBase64,
          mimeType: imageMimeType,
        }
      }),
      config: {
        numberOfVideos: 1,
        resolution: '720p',
        aspectRatio: aspectRatio,
      },
    });

    while (!operation.done) {
      await new Promise(resolve => setTimeout(resolve, 10000));
      operation = await ai.operations.getVideosOperation({ operation: operation });
    }

    const downloadLink = operation.response?.generatedVideos?.[0]?.video?.uri;

    if (downloadLink) {
      const videoUriWithApiKey = `${downloadLink}&key=${process.env.API_KEY}`;
      return { videoUrl: videoUriWithApiKey, error: null };
    } else {
      console.error('Video generation operation failed or returned no video URI:', operation);
      return { videoUrl: null, error: operation.error?.message || 'Video generation failed.' };
    }
  } catch (err) {
    console.error('Error generating video:', err);
    let errorMessage = 'An unexpected error occurred during video generation.';

    if (err instanceof Error) {
      errorMessage = err.message;
    } else if (typeof err === 'object' && err !== null && 'message' in err) {
      errorMessage = err.message;
    }

    if (errorMessage.includes("Requested entity was not found.")) {
      errorMessage = "API key issue: Please select a valid API key from a paid GCP project. Make sure billing is enabled.";
    }

    return { videoUrl: null, error: errorMessage };
  }
};

// components/LunarNodesVisualization.tsx
const LunarNodesVisualization = () => {
  const svgRef = useRef(null);
  const zoomRef = useRef(null);
  const containerGRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [time, setTime] = useState(0);
  const [earthSpeedMultiplier, setEarthSpeedMultiplier] = useState(1);
  const [moonSpeedMultiplier, setMoonSpeedMultiplier] = useState(1);
  const [currentZoomTransform, setCurrentZoomTransform] = useState(d3.zoomIdentity);

  const width = 600;
  const height = 600;
  const centerX = width / 2;
  const centerY = height / 2;

  const renderVisualization = useCallback((currentTime) => {
    const svg = d3.select(svgRef.current);
    const defs = svg.select('defs').node() ? svg.select('defs') : svg.append('defs');
    const g = d3.select(containerGRef.current);
    g.selectAll('*').remove();

    defs.select('#sunGradient').remove();
    const sunGradient = defs.append('radialGradient')
      .attr('id', 'sunGradient')
      .attr('cx', '50%')
      .attr('cy', '50%')
      .attr('r', '50%')
      .attr('fx', '50%')
      .attr('fy', '50%');
    sunGradient.append('stop').attr('offset', '0%').attr('stop-color', '#FFFACD');
    sunGradient.append('stop').attr('offset', '100%').attr('stop-color', '#FF8C00');

    defs.select('#earthGradient').remove();
    const earthGradient = defs.append('radialGradient')
      .attr('id', 'earthGradient')
      .attr('cx', '40%')
      .attr('cy', '40%')
      .attr('r', '70%')
      .attr('fx', '20%')
      .attr('fy', '20%');
    earthGradient.append('stop').attr('offset', '0%').attr('stop-color', '#6495ED');
    earthGradient.append('stop').attr('offset', '100%').attr('stop-color', '#1E90FF');

    defs.select('#moonGradient').remove();
    const moonGradient = defs.append('radialGradient')
      .attr('id', 'moonGradient')
      .attr('cx', '40%')
      .attr('cy', '40%')
      .attr('r', '70%')
      .attr('fx', '20%')
      .attr('fy', '20%');
    moonGradient.append('stop').attr('offset', '0%').attr('stop-color', '#C0C0C0');
    moonGradient.append('stop').attr('offset', '100%').attr('stop-color', '#696969');

    const sunCircle = g.append('circle')
      .attr('r', SUN_RADIUS)
      .attr('fill', 'url(#sunGradient)')
      .attr('class', 'drop-shadow-lg');
    sunCircle.append('title').text('Sun');

    g.append('ellipse')
      .attr('rx', EARTH_ORBIT_RADIUS * 1.1)
      .attr('ry', EARTH_ORBIT_RADIUS * 0.6 * 1.1)
      .attr('fill', 'rgba(70, 130, 180, 0.25)')
      .attr('stroke', 'rgba(173, 216, 230, 0.6)')
      .attr('stroke-width', 1);

    g.append('ellipse')
      .attr('rx', EARTH_ORBIT_RADIUS)
      .attr('ry', EARTH_ORBIT_RADIUS * 0.6)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(173, 216, 230, 1)')
      .attr('stroke-dasharray', '5,5');

    const effectiveEarthOrbitalPeriod = EARTH_ORBITAL_PERIOD / earthSpeedMultiplier;
    const earthAngle = (currentTime / effectiveEarthOrbitalPeriod) * 2 * Math.PI;
    const earthX = EARTH_ORBIT_RADIUS * Math.cos(earthAngle);
    const earthY = EARTH_ORBIT_RADIUS * 0.6 * Math.sin(earthAngle);

    const earthG = g.append('g')
      .attr('transform', `translate(${earthX}, ${earthY})`);

    earthG.append('circle')
      .attr('r', EARTH_RADIUS)
      .attr('fill', 'url(#earthGradient)')
      .attr('class', 'shadow-md');

    const equatorialPlaneTiltAngle = 23.5 * (Math.PI / 180);
    earthG.append('ellipse')
      .attr('rx', EARTH_RADIUS * 1.5)
      .attr('ry', EARTH_RADIUS * 0.5)
      .attr('transform', `rotate(${equatorialPlaneTiltAngle * 180 / Math.PI})`)
      .attr('fill', 'rgba(0, 255, 0, 0.15)')
      .attr('stroke', 'rgba(0, 255, 0, 0.8)')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '2,8');

    const moonOrbitG = earthG.append('g');

    const rahuAngleOnEcliptic = 0;
    const ketuAngleOnEcliptic = Math.PI;

    const createTiltedArc = (startAngle, endAngle, direction) => {
        const points = [];
        const steps = 50;
        for (let i = 0; i <= steps; i++) {
            const angle = startAngle + (endAngle - startAngle) * (i / steps);
            const x = MOON_ORBIT_RADIUS * Math.cos(angle);
            const y = MOON_ORBIT_RADIUS * Math.sin(angle) * Math.cos(ORBIT_INCLINATION_ANGLE);
            const z = MOON_ORBIT_RADIUS * Math.sin(angle) * Math.sin(ORBIT_INCLINATION_ANGLE);
            const projectedY = y - z * 0.5 * direction;
            points.push([x, projectedY]);
        }
        const lineGenerator = d3.line();
        return lineGenerator(points);
    };

    moonOrbitG.append('path')
      .attr('d', createTiltedArc(ketuAngleOnEcliptic, 2 * Math.PI, 1))
      .attr('fill', 'none')
      .attr('stroke', 'rgba(255,255,255,0.7)')
      .attr('stroke-dasharray', '3,3')
      .attr('stroke-width', 1);

    moonOrbitG.append('path')
      .attr('d', createTiltedArc(0, ketuAngleOnEcliptic, 1))
      .attr('fill', 'none')
      .attr('stroke', 'rgba(255,255,255,1)')
      .attr('stroke-width', 1.5);

    const effectiveMoonOrbitalPeriod = MOON_ORBITAL_PERIOD / moonSpeedMultiplier;
    const moonAngle = (currentTime / effectiveMoonOrbitalPeriod) * 2 * Math.PI;
    const moonX_relative = MOON_ORBIT_RADIUS * Math.cos(moonAngle);
    const moonY_relative = MOON_ORBIT_RADIUS * Math.sin(moonAngle) * Math.cos(ORBIT_INCLINATION_ANGLE);
    const moonZ_relative = MOON_ORBIT_RADIUS * Math.sin(moonAngle) * Math.sin(ORBIT_INCLINATION_ANGLE);

    const moonY_projected = moonY_relative - moonZ_relative * 0.5;

    const moonG = moonOrbitG.append('g')
      .attr('transform', `translate(${moonX_relative}, ${moonY_projected})`);

    moonG.append('circle')
      .attr('r', MOON_RADIUS)
      .attr('fill', 'url(#moonGradient)')
      .attr('class', 'shadow-sm');

    const rahuNodeX = MOON_ORBIT_RADIUS * Math.cos(rahuAngleOnEcliptic);
    const rahuNodeY_projected = 0;

    const rahuNodeG = earthG.append('g');
    rahuNodeG.append('circle')
      .attr('cx', rahuNodeX)
      .attr('cy', rahuNodeY_projected)
      .attr('r', 8)
      .attr('fill', 'rgba(255,105,180,0.7)')
      .attr('stroke', '#FF1493')
      .attr('stroke-width', 2);

    const ketuNodeX = MOON_ORBIT_RADIUS * Math.cos(ketuAngleOnEcliptic);
    const ketuNodeY_projected = 0;

    const ketuNodeG = earthG.append('g');
    ketuNodeG.append('circle')
      .attr('cx', ketuNodeX)
      .attr('cy', ketuNodeY_projected)
      .attr('r', 8)
      .attr('fill', 'rgba(138,43,226,0.9)')
      .attr('stroke', '#9932CC')
      .attr('stroke-width', 2);

    earthG.append('line')
      .attr('x1', rahuNodeX)
      .attr('y1', rahuNodeY_projected)
      .attr('x2', ketuNodeX)
      .attr('y2', ketuNodeY_projected)
      .attr('stroke', 'rgba(255,255,255,0.9)')
      .attr('stroke-dasharray', '4,4')
      .attr('stroke-width', 1.5)
      .attr('class', 'line-of-nodes');
    
    const nodeTolerance = 0.1;
    const isNearRahu = Math.abs(moonAngle % (2 * Math.PI) - rahuAngleOnEcliptic) < nodeTolerance ||
                       Math.abs(moonAngle % (2 * Math.PI) - (rahuAngleOnEcliptic + 2 * Math.PI)) < nodeTolerance;
    const isNearKetu = Math.abs(moonAngle % (2 * Math.PI) - ketuAngleOnEcliptic) < nodeTolerance ||
                       Math.abs(moonAngle % (2 * Math.PI) - (ketuAngleOnEcliptic + 2 * Math.PI)) < nodeTolerance;

    if (isNearRahu) {
        rahuNodeG.select('circle')
          .transition().duration(200)
          .attr('r', 12)
          .attr('fill', 'rgba(255,105,180,0.9)');
    } else {
      rahuNodeG.select('circle')
          .transition().duration(200)
          .attr('r', 8)
          .attr('fill', 'rgba(255,105,180,0.7)');
    }
    if (isNearKetu) {
        ketuNodeG.select('circle')
          .transition().duration(200)
          .attr('r', 12)
          .attr('fill', 'rgba(138,43,226,1)');
    } else {
      ketuNodeG.select('circle')
          .transition().duration(200)
          .attr('r', 8)
          .attr('fill', 'rgba(138,43,226,0.9)');
    }

    const currentEarthAngleNormalized = (earthAngle + 2 * Math.PI) % (2 * Math.PI);

    ZODIAC_SIGNS.forEach((zodiac) => {
      const zodiacAngle = zodiac.startAngle;
      const anglePerSign = (2 * Math.PI) / 12;

      const zodiacX = (EARTH_ORBIT_RADIUS + ZODIAC_RADIUS_OFFSET) * Math.cos(zodiacAngle);
      const zodiacY = (EARTH_ORBIT_RADIUS + ZODIAC_RADIUS_OFFSET) * 0.6 * Math.sin(zodiacAngle);

      let isCurrentZodiac = false;
      const endAngle = (zodiac.startAngle + anglePerSign) % (2 * Math.PI);

      if (zodiac.startAngle < endAngle) {
        isCurrentZodiac = (currentEarthAngleNormalized >= zodiac.startAngle && currentEarthAngleNormalized < endAngle);
      } else {
        isCurrentZodiac = (currentEarthAngleNormalized >= zodiac.startAngle || currentEarthAngleNormalized < endAngle);
      }
      
      const zodiacGroup = g.append('g')
        .attr('transform', `translate(${zodiacX}, ${zodiacY})`);

      const rectSize = parseInt(ZODIAC_SYMBOL_FONT_SIZE, 10) * 1.5;
      zodiacGroup.append('rect')
        .attr('x', -rectSize / 2)
        .attr('y', -rectSize / 2)
        .attr('width', rectSize)
        .attr('height', rectSize)
        .attr('fill', 'transparent')
        .attr('pointer-events', 'all')
        .append('title')
        .text(`${zodiac.name} (Starts: ${zodiac.startDate})`);

      zodiacGroup.append('text')
        .attr('fill', isCurrentZodiac ? '#FFD700' : '#888888')
        .attr('font-size', isCurrentZodiac ? ZODIAC_SYMBOL_FONT_SIZE : '16px')
        .attr('font-weight', isCurrentZodiac ? 'bold' : 'normal')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('text-shadow', '1px 1px 2px black')
        .text(zodiac.symbol);

      if (isCurrentZodiac) {
        g.append('line')
          .attr('x1', earthX)
          .attr('y1', earthY)
          .attr('x2', zodiacX)
          .attr('y2', zodiacY)
          .attr('stroke', '#FFD700')
          .attr('stroke-width', 1)
          .attr('stroke-dasharray', '2,2');
      }
    });

  }, [centerX, centerY, earthSpeedMultiplier, moonSpeedMultiplier]);

  useEffect(() => {
    let animationFrameId;

    const animate = () => {
      if (isPlaying) {
        setTime((prevTime) => prevTime + 1);
      }
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying]);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    const g = d3.select(containerGRef.current);

    zoomRef.current = d3.zoom()
      .scaleExtent([0.5, 5])
      .translateExtent([[-width, -height], [2 * width, 2 * height]]) 
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setCurrentZoomTransform(event.transform);
      });

    svg.call(zoomRef.current);
    zoomRef.current.transform(svg, d3.zoomIdentity.translate(centerX, centerY));

  }, [width, height, centerX, centerY]);

  useEffect(() => {
    renderVisualization(time);
  }, [time, renderVisualization]);

  const togglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const changeEarthSpeed = (delta) => {
    setEarthSpeedMultiplier(prev => Math.max(0.1, Math.min(10.0, parseFloat((prev + delta).toFixed(2)))));
  };

  const changeMoonSpeed = (delta) => {
    setMoonSpeedMultiplier(prev => Math.max(0.1, Math.min(10.0, parseFloat((prev + delta).toFixed(2)))));
  };

  const zoomIn = () => {
    if (zoomRef.current) {
      d3.select(svgRef.current).transition().duration(250).call(zoomRef.current.scaleBy, 1.2);
    }
  };

  const zoomOut = () => {
    if (zoomRef.current) {
      d3.select(svgRef.current).transition().duration(250).call(zoomRef.current.scaleBy, 0.8);
    }
  };

  const resetView = () => {
    if (zoomRef.current) {
      d3.select(svgRef.current).transition().duration(250).call(zoomRef.current.transform, d3.zoomIdentity.translate(centerX, centerY)); 
    }
  };

  return React.createElement("div", {
    className: "relative w-full h-full flex flex-col items-center justify-center bg-gray-900 rounded-lg p-2 overflow-hidden"
  }, React.createElement("svg", {
    ref: svgRef,
    width: "100%",
    height: "100%",
    viewBox: `0 0 ${width} ${height}`
  }, React.createElement("defs", null), React.createElement("g", {
    ref: containerGRef
  })), React.createElement("div", {
    className: "absolute bottom-4 flex flex-wrap justify-center items-center space-x-2 space-y-2"
  }, React.createElement("button", {
    onClick: togglePlay,
    className: "px-3 py-1 bg-sun-yellow text-space-blue font-bold rounded-full shadow-lg hover:bg-yellow-400 transition duration-300 ease-in-out text-lg",
    "aria-label": isPlaying ? 'Pause animation' : 'Play animation'
  }, isPlaying ? '⏸' : '▶'), React.createElement("span", {
    className: "text-white text-sm"
  }, "Earth:"), React.createElement("button", {
    onClick: () => changeEarthSpeed(-0.25),
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Decrease Earth Speed"
  }, "\u2212"), React.createElement("span", {
    className: "text-white text-sm"
  }, earthSpeedMultiplier.toFixed(2), "x"), React.createElement("button", {
    onClick: () => changeEarthSpeed(0.25),
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Increase Earth Speed"
  }, "+"), React.createElement("span", {
    className: "text-white text-sm"
  }, "Moon:"), React.createElement("button", {
    onClick: () => changeMoonSpeed(-0.25),
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Decrease Moon Speed"
  }, "\u2212"), React.createElement("span", {
    className: "text-white text-sm"
  }, moonSpeedMultiplier.toFixed(2), "x"), React.createElement("button", {
    onClick: () => changeMoonSpeed(0.25),
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Increase Moon Speed"
  }, "+"), React.createElement("button", {
    onClick: zoomIn,
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Zoom In"
  }, "+"), React.createElement("button", {
    onClick: zoomOut,
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-lg",
    "aria-label": "Zoom Out"
  }, "\u2212"), React.createElement("button", {
    onClick: resetView,
    className: "px-3 py-1 bg-blue-600 text-white font-bold rounded-full shadow-lg hover:bg-blue-700 transition duration-300 ease-in-out text-sm",
    "aria-label": "Reset View"
  }, "\uD83D\uDD04")), React.createElement("p", {
    className: "absolute top-4 right-4 text-sm text-gray-100"
  }, "Time: ", time));
};

// components/LunarNodesDescription.tsx
const LunarNodesDescription = () => {
  return React.createElement("div", {
    className: "prose prose-invert max-w-none text-gray-200 leading-relaxed space-y-4 text-sm md:text-base lg:text-sm xl:text-base flex-grow overflow-y-auto pr-2"
  }, React.createElement("p", {
    className: "text-sm md:text-base lg:text-sm xl:text-base"
  }, "Ever wondered why eclipses don't happen every month? Or heard mysterious names like ", React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu"), " and ", React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu"), " in ancient sky-watching stories? Get ready to uncover one of the universe's cool secrets: the Lunar Nodes!"), React.createElement("h4", {
    className: "text-lg font-semibold text-sun-yellow mt-4"
  }, "What are Lunar Nodes (Scientifically Speaking)?"), React.createElement("p", null, "Imagine ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth"), " orbiting the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), " \u2013 that path is called the ", React.createElement("span", {
    className: "text-ecliptic-light-blue font-bold"
  }, "ecliptic plane"), ". Now, picture our ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " orbiting ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth"), ". But here's the twist: the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon's"), " orbit isn't perfectly flat with ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth's"), " orbit around the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), ". It's tilted by about 5 degrees!"), React.createElement("p", null, "Because of this tilt, the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon's"), " orbital path crosses the ", React.createElement("span", {
    className: "text-ecliptic-light-blue font-bold"
  }, "ecliptic plane"), " at two special points. These two points are what astronomers call the ", React.createElement("span", {
    className: "text-white font-bold"
  }, "Lunar Nodes"), "."), React.createElement("ul", {
    className: "list-disc pl-5"
  }, React.createElement("li", null, React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Ascending Node (North Node):"), " This is where the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " crosses the ", React.createElement("span", {
    className: "text-ecliptic-light-blue font-bold"
  }, "ecliptic plane"), ", moving from \"below\" (south) to \"above\" (north) it."), React.createElement("li", null, React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Descending Node (South Node):"), " This is the opposite point, where the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " crosses the ", React.createElement("span", {
    className: "text-ecliptic-light-blue font-bold"
  }, "ecliptic plane"), ", moving from \"above\" (north) to \"below\" (south) it.")), React.createElement("p", null, "These nodes aren't physical objects like planets or stars; they are mathematical points in space. However, they are super important because eclipses (both solar and lunar) can only happen when the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " is very close to one of these nodes during its orbit!"), React.createElement("h4", {
    className: "text-lg font-semibold text-sun-yellow mt-4"
  }, "Rahu & Ketu: The Cosmic Shadows of Ancient India"), React.createElement("p", null, "Long before modern astronomy, ancient Indian (Hindu) astronomers keenly observed the skies. They recognized the crucial role of these intersection points for celestial events, especially eclipses. These skilled observers understood that when the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), ", ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), ", and ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth"), " aligned precisely along this '", React.createElement("span", {
    className: "text-white font-bold"
  }, "Line of Nodes"), ",' eclipses would occur. This knowledge allowed them to ", React.createElement("strong", null, "predict these dramatic celestial events"), ", which were often interpreted as powerful omens or mythological battles in popular culture."), React.createElement("p", null, "They personified these nodes, giving them profound mythological and astrological significance as ", React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu"), " and ", React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu"), ":"), React.createElement("ul", {
    className: "list-disc pl-5"
  }, React.createElement("li", null, React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu (North Node):"), " Corresponds to the Ascending Lunar Node. In mythology, Rahu is often depicted as the head of a cosmic serpent, constantly seeking to \"swallow\" the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), " or ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), ", thus causing eclipses. It's associated with desire, ambition, and worldly pursuits."), React.createElement("li", null, React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu (South Node):"), " Corresponds to the Descending Lunar Node. Ketu is the tail of the cosmic serpent. It represents detachment, spiritual pursuits, and letting go of material desires.")), React.createElement("p", null, "Together, ", React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu"), " and ", React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu"), " are seen as powerful \"shadow planets\" (or Chhaya Grahas) that influence human destiny and major events, even though they have no physical body. They are always exactly 180 degrees opposite each other in the sky."), React.createElement("h4", {
    className: "text-lg font-semibold text-sun-yellow mt-4"
  }, "Global Understanding of Lunar Nodes"), React.createElement("p", null, "It's fascinating to note that other ancient civilizations also independently discovered and tracked these lunar nodes to predict eclipses. The ", React.createElement("strong", null, "Babylonians"), ", the ", React.createElement("strong", null, "ancient Chinese"), ", and the ", React.createElement("strong", null, "Greeks"), " were all aware of these crucial mathematical points in space. While they had different names or mythical stories for these celestial mechanics, their understanding of the nodes was key to mastering the prediction of solar and lunar eclipses, demonstrating a universal quest to comprehend the cosmos."), React.createElement("h4", {
    className: "text-lg font-semibold text-sun-yellow mt-4"
  }, "Why are they important?"), React.createElement("p", null, "Beyond mythology, understanding lunar nodes helps us predict eclipses! When the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), ", ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth"), ", and ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " align perfectly ", React.createElement("em", null, "and"), " the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " is at or near one of its nodes, we get to witness the breathtaking spectacle of an eclipse. Without the nodes, the ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " would simply pass above or below the ", React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), "/", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth's"), " shadow, and no eclipse would occur."), React.createElement("p", null, "So, the next time you hear about ", React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu"), " and ", React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu"), ", remember they're not just ancient myths, but fascinating pointers in space that reveal the hidden mechanics of our solar system!"), React.createElement("p", {
    className: "text-xs text-gray-400 mt-4"
  }, React.createElement("span", {
    className: "text-sun-yellow font-bold"
  }, "Sun"), " | ", React.createElement("span", {
    className: "text-earth-blue font-bold"
  }, "Earth"), " | ", React.createElement("span", {
    className: "text-moon-gray font-bold"
  }, "Moon"), " | ", React.createElement("span", {
    className: "text-ecliptic-light-blue font-bold"
  }, "Ecliptic Plane"), " | ", React.createElement("span", {
    className: "text-equatorial-green font-bold"
  }, "Equatorial Plane"), " | ", React.createElement("span", {
    className: "text-rahu-pink font-bold"
  }, "Rahu"), " | ", React.createElement("span", {
    className: "text-ketu-purple font-bold"
  }, "Ketu"), " | ", React.createElement("span", {
    className: "text-gray-400 font-bold"
  }, "Zodiac Signs")));
};

// components/VideoGenerator.tsx
const VideoGenerator = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageBase64, setImageBase64] = useState(undefined);
  const [imageMimeType, setImageMimeType] = useState(undefined);
  const [prompt, setPrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState(null);
  const [error, setError] = useState(null);
  const [apiKeySelected, setApiKeySelected] = useState(false);

  const fileInputRef = useRef(null);

  const checkApiKeyStatus = useCallback(async () => {
    // window.aistudio will only be available if running in Google AI Studio or similar environments
    // For local testing, process.env.API_KEY needs to be available or manually handled.
    // Assuming aistudio is available if the app is hosted in AI Studio's environment.
    if (typeof window !== 'undefined' && window.aistudio && typeof window.aistudio.hasSelectedApiKey === 'function') {
      const hasKey = await window.aistudio.hasSelectedApiKey();
      setApiKeySelected(hasKey);
    } else {
      console.warn('window.aistudio.hasSelectedApiKey is not available. Ensure API_KEY is set in your environment if running locally for Veo.');
      // For local development without AI Studio, if process.env.API_KEY is defined in the environment
      // (e.g., via a bundler that injects it), we can assume a key is "selected" for initial attempts.
      // Otherwise, the Veo part will likely fail until a key is somehow provided.
      // As per guidelines, process.env.API_KEY is assumed to be available.
      if (process.env.API_KEY) {
        setApiKeySelected(true);
      } else {
        setApiKeySelected(false); // No key selected if aistudio API is missing and no env key
      }
    }
  }, []);

  useEffect(() => {
    checkApiKeyStatus();
  }, [checkApiKeyStatus]);

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setImageMimeType(file.type);
      try {
        const base64 = await blobToBase64(file);
        setImageBase64(base64);
        setError(null);
      } catch (e) {
        setError(e.message || 'Failed to convert image to base64.');
        setImageBase64(undefined);
      }
    } else {
      setSelectedFile(null);
      setImageBase64(undefined);
      setImageMimeType(undefined);
    }
  };

  const handleSelectApiKey = async () => {
    if (typeof window !== 'undefined' && window.aistudio && typeof window.aistudio.openSelectKey === 'function') {
      await window.aistudio.openSelectKey();
      // Assume success after triggering the dialog, as per guidelines.
      setApiKeySelected(true);
      setError(null);
    } else {
      setError('AI Studio API Key selection not available. Please ensure your API_KEY environment variable is set manually if running outside AI Studio.');
    }
  };

  const handleGenerateVideo = async () => {
    setError(null);
    setGeneratedVideoUrl(null);

    // If API key is not selected, prompt user
    if (!apiKeySelected) {
      // Try to open the dialog, but also check if API_KEY is set via env if not in AI Studio
      await handleSelectApiKey(); 
      // Re-check status based on aistudio or env var
      const hasKeyAfterAttempt = (typeof window !== 'undefined' && window.aistudio && await window.aistudio.hasSelectedApiKey()) || !!process.env.API_KEY;
      if (!hasKeyAfterAttempt) {
        setError('Please select an API key or ensure process.env.API_KEY is defined to proceed with video generation.');
        return;
      }
      setApiKeySelected(hasKeyAfterAttempt); // Update state if key becomes available
    }

    if (!prompt.trim() && !imageBase64) {
      setError('Please provide a text prompt or upload an image.');
      return;
    }

    setIsLoading(true);
    try {
      const { videoUrl, error: genError } = await generateVideo({
        prompt: prompt.trim(),
        imageBase64: imageBase64,
        imageMimeType: imageMimeType,
        aspectRatio: aspectRatio,
      });

      if (genError) {
        setError(genError);
        if (genError.includes("Requested entity was not found.")) {
          setApiKeySelected(false); // Reset API key state, user needs to re-select
        }
      } else if (videoUrl) {
        setGeneratedVideoUrl(videoUrl);
      }
    } catch (e) {
      setError(e.message || 'An unexpected error occurred during video generation.');
    } finally {
      setIsLoading(false);
    }
  };

  return React.createElement("div", {
    className: "flex flex-col space-y-6"
  }, !apiKeySelected && React.createElement("div", {
    className: "bg-red-700 bg-opacity-30 p-4 rounded-lg text-center border border-red-500"
  }, React.createElement("p", {
    className: "text-red-300 mb-4"
  }, "A paid API key is required for Veo video generation. Please select one from your Google Cloud Project."), React.createElement("button", {
    onClick: handleSelectApiKey,
    className: "px-8 py-3 bg-red-600 text-white font-bold rounded-full shadow-lg hover:bg-red-700 transition duration-300 ease-in-out",
    disabled: isLoading
  }, "Select API Key"), React.createElement("p", {
    className: "mt-4 text-sm text-red-400"
  }, "For billing details, visit", ' ', React.createElement("a", {
    href: "https://ai.google.dev/gemini-api/docs/billing",
    target: "_blank",
    rel: "noopener noreferrer",
    className: "text-red-200 underline hover:text-red-100"
  }, "ai.google.dev/gemini-api/docs/billing"))), React.createElement("div", {
    className: "grid grid-cols-1 md:grid-cols-2 gap-6"
  }, React.createElement("div", {
    className: "flex flex-col space-y-4"
  }, React.createElement("label", {
    htmlFor: "file-upload",
    className: "block text-gray-300 text-lg font-medium"
  }, "Upload a reference image (optional):"), React.createElement("input", {
    type: "file",
    id: "file-upload",
    accept: "image/*",
    onChange: handleFileChange,
    ref: fileInputRef,
    className: "block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-500 file:text-white hover:file:bg-indigo-600",
    disabled: isLoading
  }), selectedFile && React.createElement("p", {
    className: "text-sm text-gray-400"
  }, "Selected: ", selectedFile.name), imageBase64 && React.createElement("div", {
    className: "mt-4"
  }, React.createElement("img", {
    src: `data:${imageMimeType};base64,${imageBase64}`,
    alt: "Uploaded Preview",
    className: "max-w-xs h-auto rounded-lg shadow-md mx-auto"
  }))), React.createElement("div", {
    className: "flex flex-col space-y-4"
  }, React.createElement("label", {
    htmlFor: "prompt-input",
    className: "block text-gray-300 text-lg font-medium"
  }, "Describe your video concept:"), React.createElement("textarea", {
    id: "prompt-input",
    value: prompt,
    onChange: (e) => setPrompt(e.target.value),
    placeholder: "e.g., 'A nebulous galaxy forming in space' or 'An astronaut floating around the moon'",
    rows: 4,
    className: "w-full p-3 rounded-lg bg-gray-700 text-white border border-gray-600 focus:ring-indigo-500 focus:border-indigo-500 transition duration-200",
    disabled: isLoading
  }), React.createElement("label", {
    className: "block text-gray-300 text-lg font-medium mt-4"
  }, "Aspect Ratio:"), React.createElement("div", {
    className: "flex space-x-4"
  }, React.createElement("label", {
    className: "inline-flex items-center"
  }, React.createElement("input", {
    type: "radio",
    className: "form-radio text-indigo-600",
    name: "aspectRatio",
    value: "16:9",
    checked: aspectRatio === '16:9',
    onChange: () => setAspectRatio('16:9'),
    disabled: isLoading
  }), React.createElement("span", {
    className: "ml-2 text-gray-300"
  }, "16:9 (Landscape)")), React.createElement("label", {
    className: "inline-flex items-center"
  }, React.createElement("input", {
    type: "radio",
    className: "form-radio text-indigo-600",
    name: "aspectRatio",
    value: "9:16",
    checked: aspectRatio === '9:16',
    onChange: () => setAspectRatio('9:16'),
    disabled: isLoading
  }), React.createElement("span", {
    className: "ml-2 text-gray-300"
  }, "9:16 (Portrait)"))))), React.createElement("button", {
    onClick: handleGenerateVideo,
    className: "px-8 py-4 bg-indigo-600 text-white font-bold text-xl rounded-full shadow-lg hover:bg-indigo-700 transition duration-300 ease-in-out self-center min-w-[200px]",
    disabled: isLoading || !apiKeySelected || (!prompt.trim() && !imageBase64)
  }, isLoading ? React.createElement("div", {
    className: "flex items-center justify-center"
  }, React.createElement("svg", {
    className: "animate-spin -ml-1 mr-3 h-5 w-5 text-white",
    xmlns: "http://www.w3.org/2000/svg",
    fill: "none",
    viewBox: "0 0 24 24"
  }, React.createElement("circle", {
    className: "opacity-25",
    cx: "12",
    cy: "12",
    r: "10",
    stroke: "currentColor",
    strokeWidth: "4"
  }), React.createElement("path", {
    className: "opacity-75",
    fill: "currentColor",
    d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
  })), "Generating...") : `Generate Video (${VEO_MODEL_NAME})`), error && React.createElement("div", {
    className: "bg-red-500 bg-opacity-20 p-4 rounded-lg text-red-300 border border-red-400 text-center"
  }, React.createElement("p", {
    className: "font-semibold mb-2"
  }, "Error:"), React.createElement("p", null, error)), generatedVideoUrl && React.createElement("div", {
    className: "mt-8 text-center bg-gray-800 p-6 rounded-lg shadow-inner border border-gray-700"
  }, React.createElement("h3", {
    className: "text-2xl font-bold text-green-400 mb-4"
  }, "Video Generated Successfully!"), React.createElement("video", {
    src: generatedVideoUrl,
    controls: true,
    className: "max-w-full h-auto rounded-lg shadow-xl mx-auto border border-gray-600",
    style: {
      maxHeight: '500px'
    }
  }, "Your browser does not support the video tag."), React.createElement("a", {
    href: generatedVideoUrl,
    download: "generated-video.mp4",
    className: "mt-4 inline-block px-6 py-3 bg-green-600 text-white font-bold rounded-full hover:bg-green-700 transition duration-300 ease-in-out"
  }, "Download Video")));
};


// App.tsx
const App = () => {
  return React.createElement("div", {
    className: "min-h-screen bg-space-blue text-gray-100 flex flex-col items-center p-4 sm:p-6 lg:p-8"
  }, React.createElement("header", {
    className: "w-full max-w-6xl text-center py-6 mb-8"
  }, React.createElement("h1", {
    className: "text-4xl sm:text-5xl lg:text-6xl font-extrabold text-sun-yellow leading-tight"
  }, "Unveiling the Cosmic Dance: Lunar Nodes"), React.createElement("p", {
    className: "text-xl sm:text-2xl text-gray-300 mt-2 font-light"
  }, "Where Destiny Meets the Stars \u2013 Rahu & Ketu")), React.createElement("main", {
    className: "w-full max-w-6xl grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12"
  }, React.createElement("section", {
    className: "lg:col-span-2 bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-xl shadow-lg border border-gray-700 flex flex-col items-center"
  }, React.createElement("h2", {
    className: "text-3xl font-bold text-sun-yellow mb-6"
  }, "Interactive Lunar Nodes"), React.createElement("div", {
    className: "w-full h-[400px] sm:h-[500px] lg:h-[600px] relative"
  }, React.createElement(LunarNodesVisualization, null))), React.createElement("section", {
    className: "lg:col-span-1 bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-xl shadow-lg border border-gray-700 flex flex-col"
  }, React.createElement("h2", {
    className: "text-3xl font-bold text-sun-yellow mb-6"
  }, "Explore the Lore"), React.createElement(LunarNodesDescription, null))), React.createElement("section", {
    className: "w-full max-w-6xl bg-gradient-to-br from-purple-800 to-indigo-900 p-6 rounded-xl shadow-lg border border-purple-700 mt-8"
  }, React.createElement("h2", {
    className: "text-3xl font-bold text-white mb-6 text-center"
  }, "Generate Astronomical Videos with Veo!"), React.createElement("p", {
    className: "text-lg text-gray-200 mb-8 text-center"
  }, "Upload an image and add a prompt to bring your cosmic ideas to life with AI-powered video generation."), React.createElement(VideoGenerator, null)), React.createElement("footer", {
    className: "w-full max-w-6xl text-center py-8 mt-12 border-t border-gray-700 text-gray-400"
  }, React.createElement("p", null, "\u00A9 ", new Date().getFullYear(), " Stellar Insights. All rights reserved."), React.createElement("p", {
    className: "mt-2 text-sm"
  }, "Powered by Google Gemini API")));
};

// index.tsx (Entry point)
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  React.createElement(React.StrictMode, null,
    React.createElement(App, null)
  )
);