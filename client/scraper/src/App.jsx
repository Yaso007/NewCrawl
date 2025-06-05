import React, { useState } from "react";
import axios from "axios";

import "./app.css"

export default function App() {
  const [query, setQuery] = useState("");
  const [numImages, setNumImages] = useState(null);
  const [selectedSteps, setSelectedSteps] = useState([]);
  const [params, setParams] = useState({});
  const [downloadLink, setDownloadLink] = useState("");
  const [process,setProcess] = useState(false);

  const stepList = [
    { num: "1", name: "Resize" },
    { num: "2", name: "Colorconvert" },
    { num: "3", name: "GaussianBlur" },
    { num: "4", name: "Rotate" },
    { num: "5", name: "Brightness" },
    { num: "6", name: "Contrast" },
    { num: "7", name: "Saturation" },
    { num: "8", name: "Flip" },
  ];
  const desc = {
    "1":"Resize the image,  ensures consistent input dimensions for neural networks or reduces file size for faster loading.",
    "2":"Grayscale is useful for tasks focused on structure, shape, or intensity. HSV is helpful in object detection, color filtering, or segmentation.",
    "3": "Apply Gaussian Blur.Ideal for removing high-frequency noise or preparing images for edge detection, object recognition, or deep learning tasks.",
    "4":"Rotate the image by a specified angle to augment data or correct orientation. ",
    "5":"Modify the brightness of the image to simulate varying lighting conditions. This enhances the diversity of your dataset.",
    "6": "Enhance or reduce differences between light and dark areas to improve feature detection in varied lighting.",
    "7": "Change how vivid or dull the colors look. Helps the model learn from both colorful and faded images it might see in real life",
    "8":"Flip the image horizontally or vertically to add directional variety. Helps the model learn from different angles and improve accuracy."
  }
  const handleCheckbox = (e, step) => {
    const checked = e.target.checked;
    if (checked) {
      setSelectedSteps((prev) => [...prev, step.num]);
    } else {
      setSelectedSteps((prev) => prev.filter((s) => s !== step.num));
      // Remove its params too
      const newParams = { ...params };
      delete newParams[step.name.toLowerCase()];
      setParams(newParams);
    }
  };

  const handleParamChange = (stepName, value) => {
    console.log("Values got = ",stepName," ",value)
    setParams((prev) => ({
      ...prev,
      [stepName.toLowerCase()]: value,
    }));
  };

  const handleSubmit = async () => {
    const finalParams = {};

    // Build params object
    selectedSteps.forEach((stepNum) => {
      const stepName = stepList.find((s) => s.num === stepNum).name.toLowerCase();
      finalParams[stepName] = params[stepName];
    });

    const payload = {
      query,
      num_images: parseInt(numImages),
      selected_steps: selectedSteps,
      params: finalParams,
    };

    console.log(payload);
    setProcess(true)

    try {
      const res = await axios.post("http://localhost:4000/process", payload);
      setDownloadLink(res.data.download_link);
      setProcess(false)
    } catch (err) {
      console.error(err);
      alert("Something went wrong!");
    }
  };

  return (
    
    <div style={{  fontFamily: "sans-serif",marginTop:"0px"}}>
     
    <div className="navbar">
        <p> Image Scraper and Dataset Creator</p>
      </div>
      {/* Query Input */}
   
      <div className="topQuery">
            <div>
               <label htmlFor="" id="searchKey">What are you looking for</label>
              <input id="query" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter the name of the image to be searched"/>
            </div>

            {/* Num Images */}
            <div  >
              <label htmlFor=""n id="numImg">Enter the number of images</label>
              <input id="numberOfImages"
                placeholder="Enter number of images to be downloaded 1 - 1000"
                type="number"
                value={numImages}
                onChange={(e) => setNumImages(e.target.value)}
              />
            </div>

      </div>
    {/* Show selected steps in order */}
    <h3 style={{ marginTop: 20 }}>Selected Steps Order left to right:</h3>
      <div style={{ display: "flex", gap: 10, marginBottom:10 }}>
        {selectedSteps.map((stepNum, idx) => {
          const stepName = stepList.find((s) => s.num === stepNum).name;
          return (
           <>
            <div
              key={idx}
              style={{
                padding: "10px",
                marginLeft:"20px",
                background: "#0000",
                borderRadius: 5,
                minWidth: 80,
                textAlign: "center",
                border:"1px solid black"
              }}
            >
              {stepName} 
            </div>
           
           </>
          );
        })}
      </div>

      {/* Step Selection */}
      <h3 style={{ marginTop: 20 }}>Select Steps:</h3>
      <div className="gridCard">

      {stepList.map((step) => (
        <div key={step.num} className="stepsCard" style={{"display":"flex","flexDirection":"column"}}>
          <label className="optionsLabel">
            <input
              type="checkbox"
              checked={selectedSteps.includes(step.num)}
              onChange={(e) => handleCheckbox(e, step)}
            />
            {step.name}
          </label>
             {!selectedSteps.includes(step.num) && (  <p className="desc">
            {desc[step.num]}
          </p>)}
        

          {/* If selected, show param input */}
          {selectedSteps.includes(step.num) && (
            <div style={{ margin:"10px"}}>
              {step.num === "1" ? (
                <>
                 
                  <input
                    type="number"
                    placeholder="width"
                    onChange={(e) => {
                      const width = parseInt(e.target.value);
                      const height = params["resize"]?.[1] || 256;
                      handleParamChange("resize", [width, height]);
                    }}
                  />
                
                  <input
                    type="number"
                    placeholder="height"
                    onChange={(e) => {
                      const width = params["resize"]?.[0] || 256;
                      const height = parseInt(e.target.value);
                      handleParamChange("resize", [width, height]);
                    }}
                  />
                </>
              ) :step.num ==="2"? (
                <select onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))
                }>
                  <option value="" disabled>Select a color conversion method</option>
                  <option value="40">BGR to HSV</option>
                  <option value="6">BGR to GRAY</option>
              </select>
              ):step.num ==="3"?(
                <>
                  <input
                  placeholder="(odd number like 3,5,7)"
                  onChange={(e) =>
                    handleParamChange(step.name, parseFloat(e.target.value))
                  }
                  />
                </>
              
              ):step.num ==="5"?(
                <>
                   <div style={{"display":"flex"}}>
                   
                      <label>Darker</label><input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))}
              
              /><label>Lighter</label>
                  </div>
                
                </>
              
              
              ):step.num==="4"?(
                <input
                placeholder="Enter angle for rotation (e.g., 90, 180)"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))
                }
                />):step.num ==="6"?(
                  <>
                     <div style={{"display":"flex","gap":"15"}}>
                    <label>Low</label><input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))}
  
              /><label>High</label>

                  </div>
                  
              </>
              
                ):step.num ==="7"?(
                  <>
                

                  <div style={{"display":"flex"}}>
                    <div>
                          <label>Low</label>
                    </div>
                    <div>
                      <input
                                type="range"
                                min="0.5"
                                max="2.0"
                                step="0.1"
                                onChange={(e) =>
                                  handleParamChange(step.name, parseFloat(e.target.value))}
                  
                        />
                    </div>
                   
                      <label>High</label>


                  </div>
              
              </>
                ):(
                  <select onChange={(e) =>
                    handleParamChange(step.name, parseFloat(e.target.value))
                  }>
                    <option value="" disabled>Select a color conversion method</option>
                    <option value="0">Vertical Flip</option>
                    <option value="1">Horizontal Flip</option>
                    <option value="-1">Both axes Flip</option>
                </select>
                )}
            </div>
          )}
        </div>
      ))}

      </div>
    
      {
        process? <button  style={{ marginTop: 20 }}>
        Processing Please wait.....
      </button>:<button onClick={handleSubmit} style={{ marginTop: 20 }}>
        Process Images
      </button>
      }
      {/* Submit Button */}
     

      {/* Download Link */}
      {downloadLink && (
        <div style={{ marginTop: 20 }}>
          <a href={downloadLink} target="_blank" rel="noopener noreferrer">
            <button style={{"color":"white"}}>Download Processed Zip</button>
          </a>
        </div>
      )}
    </div>
  );
}
