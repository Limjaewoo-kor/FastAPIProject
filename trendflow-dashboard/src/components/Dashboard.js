import React, { useState, useEffect } from "react";
import api from "../api";  // ✅ `axios` 설정 파일 가져오기
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const Dashboard = ({ query, source }) => {
    const [data, setData] = useState([]);

    useEffect(() => {
        if (!query) return;

        // 🔹 API 호출 (네이버 or 티스토리)
        const endpoint = source === "naver"
            ? `/search-analyze-naver/?query=${query}&max_results=5&top_n=5`
            : `/search-analyze-tistory/?query=${query}&max_results=5&top_n=5`;

        api.get(endpoint)  // ✅ `axios.get()` 대신 `api.get()` 사용!
            .then((response) => {
                setData(response.data.data);
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
            });
    }, [query, source]);

    return (
        <div style={{ padding: "20px" }}>
            <h2>{source === "naver" ? "📊 네이버 블로그 분석" : "📊 티스토리 블로그 분석"}</h2>
            <h3>검색어: {query}</h3>

            <BarChart width={600} height={300} data={data.map((post) => ({
                name: post.title,
                긍정: post.sentiment === "긍정 😀" ? 1 : 0,
                중립: post.sentiment === "중립 😐" ? 1 : 0,
                부정: post.sentiment === "부정 😡" ? 1 : 0,
            }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="긍정" fill="green" />
                <Bar dataKey="중립" fill="gray" />
                <Bar dataKey="부정" fill="red" />
            </BarChart>

            {data.map((post, index) => (
                <div key={index} style={{
                    border: "1px solid #ccc", padding: "10px", margin: "10px",
                    textAlign: "left", borderRadius: "5px"
                }}>
                    <h3><a href={post.url} target="_blank" rel="noopener noreferrer">{post.title}</a></h3>
                    <p><strong>🔑 키워드:</strong> {post.keywords.join(", ")}</p>
                    <p><strong>📌 감성 분석:</strong> {post.sentiment}</p>
                </div>
            ))}
        </div>
    );
};

export default Dashboard;
