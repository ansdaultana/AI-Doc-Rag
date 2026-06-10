import axios from "axios"; // HTTP requests

function FileUpload() {

    const handleUpload = async (event) => {
        const file = event.target.files[0]; // selected file

        if (!file) return;

        const formData = new FormData();

        formData.append("file", file); // prepare multipart form

        try {
            const response = await axios.post(
                "http://localhost:8000/upload",
                formData
            );

            alert(response.data.message);

        } catch (error) {
            console.error(error);
            alert("Upload failed");
        }
    };

    return (
        <div>
            <h2>Upload PDF</h2>

            <input
                type="file"
                accept=".pdf"
                onChange={handleUpload}
            />
        </div>
    );
}

export default FileUpload;
