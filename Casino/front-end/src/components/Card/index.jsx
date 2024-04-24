import React, { useState } from 'react';

const Card = ({ image, zIndex, position, angle }) => {

  const [pos, setPos] = useState(position);
  const [ang, setAng] = useState(angle);

  return (
    <div style={
      {
        width: "120px", 
        zIndex: zIndex, 
        position: "absolute", 
        left: pos[0], 
        top: pos[1], 
        transform: `translate(-50%, +25%) rotate(${ang}deg)`,
      }}
    >
      <img src={image} style={{width: "100%", borderRadius: "20px"}} />
    </div>
  );
};

export default Card;