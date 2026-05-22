import React, { useState, useEffect, useCallback } from "react";
import { interactionService } from "../../api";
import { v4 as uuidv4 } from 'uuid';
import debounce from 'lodash/debounce';

const InteractionButtons = ({ post, onCommentClick }) => {
    const [likes, setLikes] = useState({
        count: post.likes_count || 0,
        is_liked: false,
    });
    const [loading, setLoading] = useState(true);

    const fetchLikeStatus = useCallback(async () => {
        try {
            const res = await interactionService.getPostLikeStatus(post.id);
            setLikes(res.data);
        } catch (err) {
            console.error("Failed to fetch like status", err);
        } finally {
            setLoading(false);
        }
    }, [post.id]);

    useEffect(() => {
        fetchLikeStatus();
    }, [fetchLikeStatus]);

    // Handle Like with Debounce and Idempotency
    const debouncedLike = useCallback(
        debounce(async (postId, currentIsLiked, originalState) => {
            const idempotencyKey = uuidv4();
            try {
                const res = await interactionService.toggleLikePost(postId, idempotencyKey);
                setLikes(res.data);
            } catch (err) {
                console.error("Like action failed", err);
                setLikes(originalState);
            }
        }, 300),
        []
    );

    const handleLike = () => {
        const originalState = { ...likes };
        const newIsLiked = !likes.is_liked;
        const newCount = newIsLiked ? likes.count + 1 : Math.max(0, likes.count - 1);

        // Optimistic UI Update
        setLikes({
            count: newCount,
            is_liked: newIsLiked,
        });

        debouncedLike(post.id, newIsLiked, originalState);
    };

    const handleShare = async () => {
        const idempotencyKey = uuidv4();
        try {
            await interactionService.sharePost(post.id, "web_share", idempotencyKey);
            alert("Post shared successfully!");
        } catch (err) {
            console.error("Share failed", err);
        }
    };

    return (
        <div className="flex items-center space-x-6 py-4 border-t border-b border-gray-100 my-4">
            <button
                onClick={handleLike}
                disabled={loading}
                className={`flex items-center space-x-2 transition duration-300 ${
                    likes.is_liked ? "text-red-500" : "text-slate-500 hover:text-red-500"
                }`}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className={`h-6 w-6 ${likes.is_liked ? "fill-current" : "fill-none"}`}
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span className="font-bold text-sm">{likes.count}</span>
            </button>

            <button
                onClick={onCommentClick}
                className="flex items-center space-x-2 text-slate-500 hover:text-blue-500 transition duration-300"
            >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span className="font-bold text-sm">Comment</span>
            </button>

            <button
                onClick={handleShare}
                className="flex items-center space-x-2 text-slate-500 hover:text-green-500 transition duration-300"
            >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                <span className="font-bold text-sm italic uppercase">Share</span>
            </button>
        </div>
    );
};

export default InteractionButtons;
