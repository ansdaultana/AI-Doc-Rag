import { useState } from "react";
import axios from "axios";

function ChatBox() {

    const [message, setMessage] = useState(""); // user input

    const [response, setResponse] = useState(""); // AI response

    const [sources, setSources] = useState([]); // source documents

    const handleAsk = async () => {

        if (!message.trim()) return;

        try {

            const res = await axios.post(
                "http://localhost:8000/chat",
                {
                    message
                }
            );

            setResponse(res.data.response);

            setSources(res.data.sources || []);

        } catch (error) {

            console.error(error);

            setResponse("Error getting response");
        }
    };

    return (
        <div>

            <h2>Ask Questions</h2>

            <textarea
                rows="4"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about uploaded documents..."
            />

            <br />

            <button onClick={handleAsk}>
                Ask
            </button>

            <h3>Answer</h3>

            <p>{response}</p>

            {sources.length > 0 && (
                <>
                    <h3>Sources</h3>

                    <ul>
                        {sources.map((source, index) => (
                            <li key={index}>
                                {source}
                            </li>
                        ))}
                    </ul>
                </>
            )}

        </div>
    );
}

export default ChatBox;
