'use client';

import { useEffect, useState } from 'react';

const images = [
  '/gears.svg',
  '/cube.svg',
  '/squares.svg',
  '/barcode.svg',
];

const RandomBackdrop = () => {
  const [positions, setPositions] = useState<{ top: string; left: string; src: string }[]>([]);

  useEffect(() => {
    const newPositions = images.map((src) => ({
      src,
      top: `${Math.random() * 100}vh`,
      left: `${Math.random() * 100}vw`,
    }));
    setPositions(newPositions);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden" style={{ zIndex: 0}}>
      {positions.map((pos, index) => (
        <img
          key={index}
          src={pos.src}
          alt={`Random SVG ${index}`}
          className="absolute"
          style={{ top: pos.top, left: pos.left, width: '50px', height: '50px' }}
        />
      ))}
    </div>
  );
};

export default RandomBackdrop;