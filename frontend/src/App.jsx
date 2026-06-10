import "./App.css";

import FileUpload from "./components/FileUpload";
import ChatBox from "./components/ChatBox";

function App() {
  return (
    <div className="container">
      <h1>📚 AI Documentation Assistant</h1>

      <div className="card">
        <FileUpload />
      </div>

      <div className="card">
        <ChatBox />
      </div>
    </div>
  );
}

export default App;