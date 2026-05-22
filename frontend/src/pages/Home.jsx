import { useState, useEffect } from "react";
import { blogService } from "../api";
import PostCard from "../components/PostCard";
import Layout from "../components/Layout";
import { useToast } from "../context/ToastContext";

function Home() {
    const [posts, setPosts] = useState([]);
    const [content, setContent] = useState("");
    const [title, setTitle] = useState("");
    const [image, setImage] = useState(null);
    const [preview, setPreview] = useState(null); // Preview state
    const [isCreating, setIsCreating] = useState(false);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    
    const { addToast } = useToast();

    const getPosts = (query = "") => {
        blogService.getPosts(query)
            .then((res) => res.data)
            .then((data) => {
                // DRF Paginated Response puts arrays in data.results
                setPosts(data.results !== undefined ? data.results : data);
            })
            .catch(() => addToast("Failed to fetch research feed.", "error"));
    };

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            getPosts(searchQuery);
        }, 500);

        return () => clearTimeout(delayDebounceFn);
    }, [searchQuery]);

    const deletePost = (id) => {
        if (window.confirm("Are you sure you want to delete this citation?")) {
            blogService.deletePost(id)
                .then((res) => {
                    if (res.status === 204) {
                        addToast("Citation deleted successfully.", "info");
                        setPosts(posts.filter(post => post.id !== id));
                    }
                })
                .catch(() => addToast("Failed to delete post.", "error"));
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    const createPost = (e) => {
        e.preventDefault();
        setLoading(true);
        
        const formData = new FormData();
        formData.append("title", title);
        formData.append("content", content);
        if (image) {
            formData.append("image", image);
        }

        blogService.createPost(formData)
            .then((res) => {
                if (res.status === 201) {
                    addToast("Research published successfully!", "success");
                    setTitle("");
                    setContent("");
                    setImage(null);
                    setPreview(null);
                    setIsCreating(false);
                    getPosts();
                }
            })
            .catch(() => addToast("Failed to publish research.", "error"))
            .finally(() => setLoading(false));
    };

    return (
        <Layout>
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b-2 border-red-700 pb-6 gap-4">
                <div>
                    <h1 className="text-4xl font-serif font-bold text-slate-900 tracking-tight">Research Feed</h1>
                    <p className="text-slate-500 mt-2 font-sans text-sm uppercase tracking-wide">Recent Publications & Findings</p>
                </div>
                <div className="flex w-full md:w-auto items-center gap-4">
                    <div className="relative flex-grow md:w-64">
                        <input
                            type="text"
                            placeholder="Search papers..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="bg-white border border-gray-300 w-full py-3 px-4 text-slate-900 text-sm focus:outline-none focus:border-red-700 focus:ring-0 transition font-sans rounded-none"
                        />
                        <svg className="w-4 h-4 text-slate-400 absolute right-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </div>
                    <button 
                        onClick={() => setIsCreating(!isCreating)}
                        className="bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-8 rounded-none shadow-sm transition duration-300 font-sans uppercase tracking-widest text-xs whitespace-nowrap"
                    >
                        {isCreating ? "Discard Draft" : "Submit Paper"}
                    </button>
                </div>
            </div>

            {/* Create Post Form */}
            {isCreating && (
                <div className="bg-white border border-gray-200 p-10 shadow-sm mb-16 animate-fade-in-down">
                    <h2 className="text-2xl font-serif font-bold mb-8 text-slate-900 flex items-center gap-3">
                         Submit New Finding
                    </h2>
                    <form onSubmit={createPost}>
                        <div className="mb-6">
                            <label htmlFor="title" className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">Title</label>
                            <input
                                type="text"
                                id="title"
                                required
                                onChange={(e) => setTitle(e.target.value)}
                                value={title}
                                className="bg-white border border-gray-300 w-full py-4 px-5 text-slate-900 leading-tight focus:outline-none focus:border-red-700 focus:ring-0 transition font-serif text-xl placeholder-gray-400 rounded-none"
                                placeholder="Enter paper title..."
                            />
                        </div>
                        
                        <div className="mb-6">
                            <label htmlFor="image" className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">Figure / Illustration (Optional)</label>
                            <div className="flex items-start gap-4">
                                <input
                                    type="file"
                                    id="image"
                                    accept="image/*"
                                    onChange={handleImageChange}
                                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 transition mb-2"
                                />
                            </div>
                            {/* Image Preview Area */}
                            {preview && (
                                <div className="mt-4 border border-gray-200 p-2 inline-block">
                                    <p className="text-xs uppercase font-bold text-slate-400 mb-2">Preview</p>
                                    <img src={preview} alt="Preview" className="h-40 object-contain" />
                                </div>
                            )}
                        </div>

                        <div className="mb-8">
                            <label htmlFor="content" className="block text-slate-700 text-xs font-bold mb-2 font-sans uppercase tracking-widest">Abstract / Content</label>
                            <textarea
                                id="content"
                                required
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className="bg-white border border-gray-300 w-full py-4 px-5 text-slate-900 leading-relaxed focus:outline-none focus:border-red-700 focus:ring-0 h-56 transition font-serif text-lg placeholder-gray-400 resize-none rounded-none"
                                placeholder="Summarize your findings..."
                            ></textarea>
                        </div>
                        <div className="flex justify-end">
                            <button 
                                type="submit" 
                                disabled={loading}
                                className="bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-10 transition duration-300 font-sans uppercase tracking-widest text-xs rounded-none"
                            >
                                {loading ? "Publishing..." : "Publish Findings"}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Posts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                {posts.length > 0 ? (
                    posts.map((post) => (
                        <PostCard key={post.id} post={post} onDelete={deletePost} />
                    ))
                ) : (
                    <p className="text-slate-500 text-center col-span-2 py-20 font-serif italic text-lg border border-dashed border-gray-300">
                        No research papers available.
                    </p>
                )}
            </div>
        </Layout>
    );
}

export default Home;
