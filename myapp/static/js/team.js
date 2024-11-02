function toggleReplyBox(commentId) {
    var replyBox = document.querySelector('#reply-box-' + commentId);
    if (replyBox.style.display === 'none' || replyBox.style.display === '') {
        replyBox.style.display = 'block';
    } else {
        replyBox.style.display = 'none';
    }
}


document.addEventListener('DOMContentLoaded', function() {
    

    // Show the latest competition by default
    const latestCompetitionId = document.querySelector('.competition-standings:not(.hidden)').id.replace('standings-', '');
    selectElement.value = latestCompetitionId;

    // Event listener for select dropdown
    selectElement.addEventListener('change', function() {
        showCompetition(this.value);
    });




    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    const likeLinks = document.querySelectorAll('.like-btn');
    likeLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior

            const teamId = this.dataset.teamId;
            const commentId = this.dataset.commentId;
            const childCommentId = this.dataset.childCommentId;

            let endpoint = `/toggle_team_like/`;

            if (teamId) {
                endpoint += `${teamId}/`;
            } else if (commentId) {
                endpoint += `comment/${commentId}/`;
            } else if (childCommentId) {
                endpoint += `comment/${childCommentId}/`;
            }

            const headers = new Headers({
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            });

            fetch(endpoint, {
                method: 'POST',
                headers: headers,
                credentials: 'include',
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const likeIcon = data.liked ? '<div class="comment-like"><span class="icon mdi mdi-thumb-up-outline text-danger"></span></div>' : '<div class="comment-like"><span class="icon mdi mdi-thumb-up-outline"></span></div>';
                    this.innerHTML = likeIcon;

                    // Update the like count based on the response
                    const likeCountElement = document.getElementById(`like-count-${childCommentId ? childCommentId : (teamId || commentId)}`);
                    if (likeCountElement) {
                        likeCountElement.innerText = `${data.num_likes}`;
                    }
                }
            }).catch(error => console.error('Error:', error));
        });
    });
});
