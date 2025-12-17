import { useState, useEffect } from "react";
import api from "../api";
import PostCard from "../components/PostCard";
import Layout from "../components/Layout";

function Home() {
    const [posts, setPosts] = useState([]);
    const [content, setContent] = useState("");
    const [title, setTitle] = useState("");
    const [isCreating, setIsCreating] = useState(false);

    useEffect(() => {
        getPosts();
    }, []);

    const getPosts = () => {
        api.get("/api/blog/posts/")
            .then((res) => res.data)
            .then((data) => {
                setPosts(data);
            })
            .catch((err) => alert(err));
    };

    const deletePost = (id) => {
        if (window.confirm("Are you sure you want to delete this post?")) {
            api.delete(`/api/blog/posts/${id}/`)
                .then((res) => {
                    if (res.status === 204) {
                        // Optimistic update
                        setPosts(posts.filter(post => post.id !== id));
                    }
                    else alert("Failed to delete post.");
                })
                .catch((error) => alert(error));
        }
    };

    const createPost = (e) => {
        e.preventDefault();
        api.post("/api/blog/posts/", { content, title })
            .then((res) => {
                if (res.status === 201) {
                    alert("Post created!");
                    setTitle("");
                    setContent("");
                    setIsCreating(false);
                    getPosts();
                } else alert("Failed to make post.");
            })
            .catch((err) => alert(err));
    };

    return (
        <Layout>
            {/* Header Section */}
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-800">Latest Posts</h1>
                <button 
                    onClick={() => setIsCreating(!isCreating)}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300 shadow-md"
                >
                    {isCreating ? "Cancel" : "Create New Post"}
                </button>
            </div>

            {/* Create Post Form (Collapsible) */}
            {isCreating && (
                <div className="bg-white p-6 rounded-lg shadow-md mb-8 animate-fade-in-down">
                    <h2 className="text-xl font-bold mb-4 text-gray-700">Write a New Story</h2>
                    <form onSubmit={createPost}>
                        <div className="mb-4">
                            <label htmlFor="title" className="block text-gray-700 text-sm font-bold mb-2">Title</label>
                            <input
                                type="text"
                                id="title"
                                required
                                onChange={(e) => setTitle(e.target.value)}
                                value={title}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Enter an engaging title"
                            />
                        </div>
                        <div className="mb-6">
                            <label htmlFor="content" className="block text-gray-700 text-sm font-bold mb-2">Content</label>
                            <textarea
                                id="content"
                                required
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
                                placeholder="What's on your mind?"
                            ></textarea>
                        </div>
                        <div className="flex justify-end">
                            <button 
                                type="submit" 
                                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded transition duration-300"
                            >
                                Publish
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Posts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {posts.length > 0 ? (
                    posts.map((post) => (
                        <PostCard key={post.id} post={post} onDelete={deletePost} />
                    ))
                ) : (
                    <p className="text-gray-500 text-center col-span-2 py-10">No posts yet. Be the first to write one!</p>
                )}
            </div>
        </Layout>
    );
}

export default Home;
