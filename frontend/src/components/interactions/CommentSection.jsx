import React, { useState, useEffect } from "react";
import api from "../../api";

const CommentItem = ({ comment, onReplyAdded, postId }) => {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState("");

    const handleReply = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post("/api/interactions/comments/", {
                post: postId,
                parent: comment.id,
                content: replyContent,
            });
            onReplyAdded(res.data);
            setReplyContent("");
            setShowReplyForm(false);
        } catch (err) {
            console.error("Reply failed", err);
        }
    };

    return (
        <div className="mb-6 pl-4 border-l-2 border-gray-100">
            <div className="flex items-center space-x-2 mb-2">
                <span className="font-bold text-sm text-slate-900">{comment.author.email}</span>
                <span className="text-xs text-slate-400 font-sans">
                    {new Date(comment.created_at).toLocaleDateString()}
                </span>
            </div>
            <p className="text-slate-700 font-serif mb-2">{comment.content}</p>
            
            <button 
                onClick={() => setShowReplyForm(!showReplyForm)}
                className="text-xs font-bold text-blue-800 uppercase tracking-widest hover:text-blue-600 transition duration-300"
            >
                {showReplyForm ? "Cancel Reply" : "Reply"}
            </button>

            {showReplyForm && (
                <form onSubmit={handleReply} className="mt-4">
                    <textarea
                        className="w-full p-3 border border-gray-200 focus:border-blue-500 rounded-lg outline-none transition duration-300"
                        rows="2"
                        placeholder="Write a reply..."
                        value={replyContent}
                        onChange={(e) => setReplyContent(e.target.value)}
                        required
                    />
                    <button 
                        type="submit"
                        className="mt-2 bg-blue-900 text-white px-4 py-2 text-xs font-bold uppercase tracking-widest rounded hover:bg-blue-800 transition duration-300"
                    >
                        Post Reply
                    </button>
                </form>
            )}

            {/* Nested Replies */}
            {comment.replies && comment.replies.length > 0 && (
                <div className="mt-4 space-y-4">
                    {comment.replies.map((reply) => (
                        <CommentItem key={reply.id} comment={reply} onReplyAdded={onReplyAdded} postId={postId} />
                    ))}
                </div>
            )}
        </div>
    );
};

const CommentSection = ({ postId }) => {
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState("");
    const [loading, setLoading] = useState(true);

    const fetchComments = async () => {
        try {
            const res = await api.get(`/api/interactions/comments/post_comments/?post_id=${postId}`);
            setComments(res.data);
        } catch (err) {
            console.error("Failed to fetch comments", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchComments();
    }, [postId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post("/api/interactions/comments/", {
                post: postId,
                content: newComment,
            });
            // Update comments after add
            setComments([res.data, ...comments]);
            setNewComment("");
        } catch (err) {
            console.error("Comment failed", err);
        }
    };

    if (loading) return <div className="p-4 text-center">Loading comments...</div>;

    return (
        <section className="bg-slate-50 p-6 sm:p-10 rounded-xl my-10">
            <h3 className="text-xl font-serif font-bold text-slate-900 mb-8 border-b-2 border-blue-900 inline-block pb-1">
                Discussion
            </h3>

            {/* Comment Input */}
            <form onSubmit={handleSubmit} className="mb-10">
                <textarea
                    className="w-full p-4 border border-gray-200 focus:border-blue-500 rounded-lg outline-none transition duration-300"
                    rows="3"
                    placeholder="Share your insights..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    required
                />
                <button 
                    type="submit"
                    className="mt-4 bg-slate-900 text-white px-6 py-3 font-bold uppercase text-xs tracking-widest rounded hover:bg-blue-900 transition duration-300"
                >
                    Post Comment
                </button>
            </form>

            {/* Comments List */}
            <div className="space-y-8">
                {comments.length > 0 ? (
                    comments.map((comment) => (
                        <CommentItem 
                            key={comment.id} 
                            comment={comment} 
                            onReplyAdded={() => fetchComments()} 
                            postId={postId} 
                        />
                    ))
                ) : (
                    <p className="text-slate-500 italic">No comments yet. Be the first to start the conversation.</p>
                )}
            </div>
        </section>
    );
};

export default CommentSection;
