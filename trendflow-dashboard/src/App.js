import React, { useState } from "react";
import Dashboard from "./components/Dashboard";

function App() {
    const [query, setQuery] = useState("");
    const [source, setSource] = useState(""); // "naver" or "tistory"
    const [submitted, setSubmitted] = useState(false);

    const handleSearch = (type) => {
        if (query.trim() !== "") {
            setSource(type);
            setSubmitted(true);
        } else {
            alert("검색어를 입력해주세요!");
        }
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1>📊 블로그 감성 분석</h1>

            <input
                type="text"
                placeholder="검색어 입력..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{ padding: "10px", width: "300px", fontSize: "16px" }}
            />

            <br /><br />

            <button onClick={() => handleSearch("naver")} style={{ padding: "10px 20px", marginRight: "10px" }}>
                네이버 검색
            </button>
            <button onClick={() => handleSearch("tistory")} style={{ padding: "10px 20px" }}>
                티스토리 검색
            </button>

            {submitted && <Dashboard query={query} source={source} />}
        </div>
    );
}

export default App;
