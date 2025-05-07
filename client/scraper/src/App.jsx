import React, { useState } from "react";
import axios from "axios";
import "./app.css"

export default function App() {
  const [query, setQuery] = useState("");
  const [numImages, setNumImages] = useState(5);
  const [selectedSteps, setSelectedSteps] = useState([]);
  const [params, setParams] = useState({});
  const [downloadLink, setDownloadLink] = useState("");

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

    try {
      const res = await axios.post("http://localhost:4000/process", payload);
      setDownloadLink(res.data.download_link);
    } catch (err) {
      console.error(err);
      alert("Something went wrong!");
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>Image Scraper and Dataset Creator</h1>

      {/* Query Input */}
      <div className="topQuery">
      <div>
        <label>Query: </label>
        <input id="query" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter the name of the image to be searched"/>
      </div>

      {/* Num Images */}
      <div  >
        <label>Number of Images: </label>
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
                padding: 10,
                background: "#0000",
                borderRadius: 5,
                minWidth: 80,
                textAlign: "center",
                border:"1px solid white"
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
        <div key={step.num} className="stepsCard">
          <label>
            <input
              type="checkbox"
              checked={selectedSteps.includes(step.num)}
              onChange={(e) => handleCheckbox(e, step)}
            />
            {step.name}
          </label>

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
                  <label>Darker</label><input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))}
              
              /><label>Lighter</label>
                </>
              
              
              ):step.num==="4"?(
                <input
                placeholder="Enter angle for rotation (e.g., 90, 180)"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))
                }
                />):step.num ==="6"?(
                  <>
                  <label>Low</label><input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))}
  
              /><label>High</label>
              </>
                ):step.num ==="7"?(
                  <>
                  <label>Low</label><input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                onChange={(e) =>
                  handleParamChange(step.name, parseFloat(e.target.value))}
  
              /><label>High</label>
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
    
      

      {/* Submit Button */}
      <button onClick={handleSubmit} style={{ marginTop: 20 }}>
        Process Images
      </button>

      {/* Download Link */}
      {downloadLink && (
        <div style={{ marginTop: 20 }}>
          <a href={downloadLink} target="_blank" rel="noopener noreferrer">
            <button>Download Processed Zip</button>
          </a>
        </div>
      )}
    </div>
  );
}
