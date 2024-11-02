// document.addEventListener('DOMContentLoaded', function () {
//     let currentPost = 1;
//     const totalPosts = {{ posts|length }};

//     const btnPrev = document.querySelector('button.prev');
//     const btnNext = document.querySelector('button.next');

//     btnPrev.addEventListener('click', function() { navigatePosts(-1); });
//     btnNext.addEventListener('click', function() { navigatePosts(1); });

//     function navigatePosts(direction) {
//         document.getElementById('post-' + currentPost).classList.remove('active');
//         currentPost += direction;
//         if (currentPost > totalPosts) { currentPost = 1; }
//         if (currentPost < 1) { currentPost = totalPosts; }
//         document.getElementById('post-' + currentPost).classList.add('active');
//     };
// });