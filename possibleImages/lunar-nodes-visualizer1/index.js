
import React, { useRef, useEffect, useState, useCallback } from 'react';
import ReactDOM from 'react-dom/client';
import * as d3 from 'd3';

console.log('index.js script started.');

// constants.ts (Consolidated)
const LUNAR_NODES_MODEL = 'gemini-3-flash-preview'; // This constant is kept for context but the model is not called in this app.
const SUN_RADIUS = 30;
const EARTH_ORBIT_RADIUS = 200;
const EARTH_RADIUS = 10;
const MOON_ORBIT_RADIUS = 40;
const MOON_RADIUS = 5;
const ORBIT_INCLINATION_ANGLE = 5.2 * (Math.PI / 180);
const EARTH_ORBITAL_PERIOD = 365 * 100;
const MOON_ORBITAL_PERIOD = 27 * 100;
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

// components/LunarNodesVisualization.tsx (Consolidated)
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

// components/LunarNodesDescription.tsx (Consolidated)
const LunarNodesDescription = () => {
  const zodiacLegendContent = ZODIAC_SIGNS.map((sign, index) =>
    React.createElement(React.Fragment, { key: sign.name },
      React.createElement("span", { className: "font-bold" }, sign.symbol),
      ` ${sign.name}`,
      index < ZODIAC_SIGNS.length - 1 ? ` | ` : ''
    )
  );

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
  }, "ecliptic plane"), ", moving from \"above\" (north) to \"below\" (south) it."))), React.createElement("p", null, "These nodes aren't physical objects like planets or stars; they are mathematical points in space. However, they are super important because eclipses (both solar and lunar) can only happen when the ", React.createElement("span", {
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
  }, "Ketu (South Node):"), " Corresponds to the Descending Lunar Node. Ketu is the tail of the cosmic serpent. It represents detachment, spiritual pursuits, and letting go of material desires."))), React.createElement("p", null, "Together, ", React.createElement("span", {
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
  }, "Ketu")),
    React.createElement("p", {
      className: "text-xs text-gray-400 mt-2"
    },
      React.createElement("span", { className: "font-bold" }, "Zodiac Signs: "),
      zodiacLegendContent
    )));
};

// ErrorBoundary component to catch rendering errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return React.createElement("div", {
        className: "flex flex-col items-center justify-center min-h-screen bg-red-900 text-white p-4 font-sans"
      },
        React.createElement("h2", { className: "text-2xl font-bold mb-4" }, "Oops! Something went wrong."),
        React.createElement("p", { className: "mb-2" }, this.state.error && this.state.error.toString()),
        React.createElement("details", { className: "whitespace-pre-wrap text-sm text-red-100 bg-red-800 p-4 rounded-md mt-4 max-w-lg overflow-auto" },
          React.createElement("summary", { className: "cursor-pointer font-semibold" }, "Click for Error Details"),
          React.createElement("p", { className: "mt-2" }, this.state.errorInfo && this.state.errorInfo.componentStack)
        )
      );
    }

    return this.props.children;
  }
}

// App.tsx (Consolidated)
const App = () => {
  console.log('App component rendering.');
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
  }, "Explore the Lore"), React.createElement(LunarNodesDescription, null)))), React.createElement("footer", {
    className: "w-full max-w-6xl text-center py-8 mt-12 border-t border-gray-700 text-gray-400"
  }, React.createElement("p", null, "\u00A9 ", new Date().getFullYear(), " Stellar Insights. All rights reserved."), React.createElement("p", {
    className: "mt-2 text-sm"
  }, "Powered by Google Gemini API")));
};

// index.tsx (Entry point)
const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error("Could not find root element to mount to");
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  React.createElement(React.StrictMode, null,
    React.createElement(ErrorBoundary, null, // Wrap App with ErrorBoundary
      React.createElement(App, null)
    )
  )
);
