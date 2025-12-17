import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api from "../api";
import Layout from "../components/Layout";

function PostDetail() {
    const { id } = useParams();
    const [post, setPost] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        getPost();
    }, [id]);

    const getPost = async () => {
        try {
            const res = await api.get(`/api/blog/posts/${id}/`);
            setPost(res.data);
        } catch (err) {
            alert("Post not found!");
            navigate("/");
        }
    };

    if (!post) return <Layout><div className="text-center mt-10">Loading...</div></Layout>;

    const formattedDate = new Date(post.created_at).toLocaleDateString("en-US", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return (
        <Layout>
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="p-8">
                    <div className="uppercase tracking-wide text-sm text-blue-500 font-semibold">Blog Post</div>
                    <h1 className="block mt-1 text-3xl leading-tight font-bold text-black">{post.title}</h1>
                    <p className="text-gray-500 text-sm mt-2">By {post.author} on {formattedDate}</p>
                    
                    <div className="mt-8 text-gray-700 leading-relaxed whitespace-pre-line text-lg">
                        {post.content}
                    </div>

                    <div className="mt-8 pt-6 border-t border-gray-200">
                        <Link to="/" className="text-blue-500 hover:text-blue-800 font-semibold">
                            ← Back to Home
                        </Link>
                    </div>
                </div>
            </div>
        </Layout>
    );
}

export default PostDetail;
