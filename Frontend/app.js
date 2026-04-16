import React, { useRef, useEffect, useState } from "react";

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Open Camera
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      })
      .catch(() => alert("Camera access denied"));
  }, []);

  // Capture Image
  const capture = () => {
    setLoading(true);

    const canvas = canvasRef.current;
    const video = videoRef.current;

    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0);

    canvas.toBlob(blob => {
      let formData = new FormData();
      formData.append("file", blob, "face.jpg");

      fetch("http://127.0.0.1:8000/face-attendance", {
        method: "POST",
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          setResult(data);
          setLoading(false);
        })
        .catch(() => {
          alert("Error connecting backend");
          setLoading(false);
        });
    }, "image/jpeg");
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>📸 Face Attendance System</h2>

      <video ref={videoRef} autoPlay style={styles.video}></video>

      <button onClick={capture} style={styles.button}>
        {loading ? "Processing..." : "Scan Face"}
      </button>

      <canvas ref={canvasRef} style={{ display: "none" }} />

      {result && (
        <div style={styles.card}>
          {result.name ? (
            <>
              <h3 style={{ color: "green" }}>✅ Attendance Marked</h3>
              <p><b>Name:</b> {result.name}</p>
              <p><b>Type:</b> {result.type}</p>
              <p><b>Time:</b> {result.time}</p>
              <p><b>Date:</b> {result.date}</p>
            </>
          ) : (
            <p>{result.msg}</p>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    textAlign: "center",
    padding: "30px",
    fontFamily: "Arial",
    background: "#f4f6f8",
    minHeight: "100vh"
  },
  title: {
    marginBottom: "20px"
  },
  video: {
    width: "320px",
    borderRadius: "12px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.2)"
  },
  button: {
    marginTop: "20px",
    padding: "12px 25px",
    fontSize: "16px",
    background: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer"
  },
  card: {
    marginTop: "25px",
    padding: "20px",
    background: "white",
    display: "inline-block",
    borderRadius: "12px",
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)"
  }
};

export default App;




