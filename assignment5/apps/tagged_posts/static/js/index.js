"use strict";
const app = Vue.createApp({
    data() {
        return {
            newPostContent: '',
            feed: [],
            tags: []
        };
    },
    methods: {
        createPost(content) {
          fetch('/tagged_posts/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: content }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
            } else {
                console.log('Success:', data.message);
                this.newPostContent = '';
                this.updateFeed();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });        },
        toggleTag(tag) {
          const index = this.tags.indexOf(tag);
          if (index > -1) {
            this.tags.splice(index, 1);
          } else {
            this.tags.push(tag);
          }
      
          let url = '/tagged_posts/api/posts';
          if (this.tags.length > 0) {
            url += '?tags=' + this.tags.join(',');
          }
      
          fetch(url)
            .then(response => response.json())
            .then(data => {
              this.feed = data;
            })
            .catch((error) => {
              console.error('Error:', error);
            });        },
        updateFeed() {
          let url = '/tagged_posts/api/posts';
          if (this.tags && this.tags.length > 0) {
            url += '?tags=' + this.tags.join(',');
          }
          fetch(url)
            .then(response => response.json())
            .then(data => {
              this.feed = data;
            })
            .catch((error) => {
              console.error('Error:', error);
            });             
          },
        submitPost(event) {
          event.preventDefault();
      
          fetch('/tagged_posts/api/posts', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({content: this.newPostContent}),
          })
          .then(response => response.json())
          .then(data => {
              // Add the new post to the beginning of the feed
              this.feed.unshift(data);
              this.newPostContent = '';
          })
          .catch((error) => {
              console.error('Error:', error);
          });        },
        deletePost(postId) {
          fetch(`/tagged_posts/api/posts/${postId}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
          })
          .then(response => response.json())
          .then(data => {
            if (data.error) {
              console.error(`Error deleting post: ${data.error}`);
            } else {
              // Remove the deleted post from the posts array
              this.posts = this.posts.filter(post => post.id !== postId);
            }
          })
          .catch(error => console.error(`Error: ${error}`));        },
    },
    created() {
        this.updateFeed();
    }
});

app.mount('#app');
app.updateFeed();
// "use strict";
// new Vue({
//     el: '#app',
//     data: {
//       newPostContent: '',
//       feed: [],
//       tags: []
//     },
//     methods: {
//         createPost: function(content) {
//             fetch('/tagged_posts/api/posts', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ content: content }),
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.error) {
//                     console.error('Error:', data.error);
//                 } else {
//                     console.log('Success:', data.message);
//                     this.newPostContent = '';
//                     this.updateFeed();
//                 }
//             })
//             .catch((error) => {
//                 console.error('Error:', error);
//             });
//           },
//       toggleTag: function(tag) {
//         const index = this.tags.indexOf(tag);
//         if (index > -1) {
//           this.tags.splice(index, 1);
//         } else {
//           this.tags.push(tag);
//         }
    
//         let url = '/tagged_posts/api/posts';
//         if (this.tags.length > 0) {
//           url += '?tags=' + this.tags.join(',');
//         }
    
//         fetch(url)
//           .then(response => response.json())
//           .then(data => {
//             this.feed = data;
//           })
//           .catch((error) => {
//             console.error('Error:', error);
//           });      },
//       updateFeed: function() {
//         let url = '/tagged_posts/api/posts';
//         if (tags && tags.length > 0) {
//           url += '?tags=' + tags.join(',');
//         }
//         fetch(url)
//           .then(response => response.json())
//           .then(data => {
//             this.feed = data;
//           })
//           .catch((error) => {
//             console.error('Error:', error);
//           });      
//         },
//         submitPost: function(event) {
//           // Prevent the default form submission behavior
//           event.preventDefault();
      
//           fetch('/tagged_posts/api/posts', {
//               method: 'POST',
//               headers: {
//                   'Content-Type': 'application/json',
//               },
//               body: JSON.stringify({content: this.newPostContent}),
//           })
//           .then(response => response.json())
//           .then(data => {
//               // Add the new post to the beginning of the feed
//               this.feed.unshift(data);
//               this.newPostContent = '';
//           })
//           .catch((error) => {
//               console.error('Error:', error);
//           });
//       },
//       deletePost(postId) {
//         fetch(`/tagged_posts/api/posts/${postId}`, {
//           method: 'DELETE',
//           headers: {
//             'Content-Type': 'application/json',
//           },
//         })
//         .then(response => response.json())
//         .then(data => {
//           if (data.error) {
//             console.error(`Error deleting post: ${data.error}`);
//           } else {
//             // Remove the deleted post from the posts array
//             this.posts = this.posts.filter(post => post.id !== postId);
//           }
//         })
//         .catch(error => console.error(`Error: ${error}`));
//       },
//     },
//     created: function() {
//       this.updateFeed();
//     }
//   });