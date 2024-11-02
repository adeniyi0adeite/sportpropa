function toggleCommentBox(postId) {
    var commentBox = document.querySelector('#comment-box-' + postId);
    if (commentBox.style.display === 'none') {
        commentBox.style.display = 'block';
    } else {
        commentBox.style.display = 'none';
    }
}

function toggleReplyBox(commentId) {
    var replyBox = document.querySelector('#reply-box-' + commentId);
    if (replyBox.style.display === 'none' || replyBox.style.display === '') {
        replyBox.style.display = 'block';
    } else {
        replyBox.style.display = 'none';
    }
}


document.addEventListener('DOMContentLoaded', function() {
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    const likeLinks = document.querySelectorAll('.like-btn');
    likeLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior

            const postId = this.dataset.postId;
            const parentCommentId = this.dataset.commentId;
            const childCommentId = this.dataset.childCommentId; // For child comments

            let endpoint = `/toggle_like/`;

            if (postId) {
                endpoint += `${postId}/`;
            } else if (parentCommentId) {
                endpoint += `comment/${parentCommentId}/`;
            } else if (childCommentId) {
                endpoint += `comment/${childCommentId}/`; // For child comments
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
                    const likeCountElement = document.getElementById(`like-count-${childCommentId ? childCommentId : (postId || parentCommentId)}`);
                    if (likeCountElement) {
                        likeCountElement.innerText = `${data.num_likes}`;
                    }
                }
            }).catch(error => console.error('Error:', error));
        });
    });

    // $('#replyModal').on('show.bs.modal', function (event) {
    //     var button = $(event.relatedTarget); // Button that triggered the modal
    //     var parentCommentId = button.data('comment-id'); // Extract info from data-* attributes
    //     var postId = '{{ post.id }}'; // Assuming you have the post ID available in the template
    //     var formAction = '{% url "add_comment" post_id=0 %}'.replace('/0/', '/' + postId + '/') + parentCommentId + '/'; // Construct the form action
    //     $(this).find('form').attr('action', formAction); // Set the form action
    //   });


    var newPictureInput = document.getElementById('new_picture');
    if (newPictureInput) {
        newPictureInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                // If a file is selected, submit the form
                var form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }

    
});

