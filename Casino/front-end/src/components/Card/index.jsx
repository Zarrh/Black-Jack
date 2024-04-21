import React, { useState } from 'react';

const Card = ({ image, zIndex, x, y }) => {

  const [pos, setPos] = useState([x, y]);

  return (
    <div style={
      {
        width: "120px", 
        zIndex: zIndex, 
        position: "absolute", 
        left: pos[0], 
        top: pos[1], 
        transform: "translate(-50%, +25%)",
      }}
    >
      <img src={image} style={{borderRadius: "20px"}} />
    </div>
  );
};

export default Card;