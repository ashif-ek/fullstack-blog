import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { blogService } from "../api";
import Layout from "../components/Layout";
import { useToast } from "../context/ToastContext";
import InteractionButtons from "../components/interactions/InteractionButtons";
import CommentSection from "../components/interactions/CommentSection";
import { useRef } from "react";

function PostDetail() {
    const { id } = useParams();
    const [post, setPost] = useState(null);
    const navigate = useNavigate();
    const { addToast } = useToast();
    const commentSectionRef = useRef(null);

    const scrollToComments = () => {
        commentSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const getPost = async () => {
        try {
            const res = await blogService.getPostDetail(id);
            setPost(res.data);
        } catch {
            addToast("Citation not found or access denied.", "error");
            navigate("/");
        }
    };

    useEffect(() => {
        getPost();
    }, [id]);

    if (!post) return <Layout><div className="text-center mt-20 text-slate-500 font-serif animate-pulse">Loading Analysis...</div></Layout>;

    const formattedDate = new Date(post.created_at).toLocaleDateString("en-US", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    return (
        <Layout>
            <div className="bg-white border border-gray-200 shadow-sm overflow-hidden mb-10">
                {post.image && (
                    <div className="w-full h-96 relative border-b border-gray-200">
                        <img src={post.image} alt={post.title} className="w-full h-full object-cover" />
                    </div>
                )}

                <div className="p-12 md:p-16">
                    <div className="uppercase tracking-widest text-xs font-bold text-blue-900 mb-4 font-sans border-b-2 border-slate-900 inline-block pb-1">Research Publication</div>
                    <h1 className="text-4xl md:text-5xl font-bold font-serif text-slate-900 leading-tight mb-6">{post.title}</h1>
                    
                    <div className="flex items-center text-slate-500 text-sm font-sans mb-12 border-b border-gray-200 pb-8">
                        <span className="font-bold text-slate-900 mr-2">{post.author}</span> 
                        <span className="mx-2 text-slate-400">•</span>
                        <span>{formattedDate}</span>
                    </div>
                    
                    <div className="prose prose-lg max-w-none text-slate-800 font-serif leading-loose">
                        {post.content.split('\n').map((paragraph, idx) => (
                             <p key={idx} className="mb-6">{paragraph}</p>
                        ))}
                    </div>

                    <InteractionButtons 
                        post={post} 
                        onCommentClick={scrollToComments} 
                    />

                    <div ref={commentSectionRef}>
                        <CommentSection postId={post.id} />
                    </div>

                    <div className="mt-16 pt-8 border-t border-gray-200 flex justify-between items-center">
                        <Link to="/" className="text-slate-500 hover:text-blue-900 font-bold text-xs uppercase tracking-widest transition duration-300 flex items-center gap-2">
                             <span className="transform -translate-x-1 group-hover:-translate-x-2 transition-transform">←</span> Return to Feed
                        </Link>
                    </div>
                </div>
            </div>
        </Layout>
    );
}

export default PostDetail;
