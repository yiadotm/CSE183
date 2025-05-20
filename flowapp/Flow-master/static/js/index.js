// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        mode: "no_textarea",
        new_post_text: "",
        user_email: user_email,
        posts: [], // Suggested.
        text: ""
        // Complete.
    };

    // Add here the various functions you need.
    app.change_mode = (mode) => {
        console.log(mode)
        app.vue.mode = mode;
        axios.post(send_text_url, {post_id: mode}).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            app.vue.text = response.data.text;
            app.vue.new_post_text = response.data.text;
            console.log(app.vue.text)
            //print(res);
            })
            
            
        
    };
            
        

    // Use this function to reindex the posts, when you get them, and when
    // you add / delete one of them.
    app.reindex = (a) => {

        let c=0;
        let idx = 0;
        for (p of a) {
            c+=1;
            p._idx = idx++;
            console.log(p);
            // Add here whatever other attributes should be part of a post.
            p.show_ppl_who_liked_post = false;
            p.likers = "";
            p.haters = "";
            p.expired_likers = true;

        // if (c==0)
        // {
        //     axios.post(send_text_url, {post_id: mode}).then(function (response) {
        //         // response.data contains the response.
        //         // response has other fields, such as status, etc; see them in the log.
        //         //let res = app.reindex(response.data.text);
        //         //print(res);
        //         })
        // }

        }
        return a;
    };

    app.reset_textarea = () => {
        app.vue.new_post_text = "";
    };

    app.add_post = () => {
        console.log(app.vue.new_post_text);
        axios.post(add_post_url, {post_text: app.vue.new_post_text}).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            let res = app.reindex(response.data.posts);
            for (let i of res) {
                console.log(i);
            }
            app.vue.posts = res;
            app.reset_textarea();
        })
    };
    app.edit_post = (_post_id) => {
        console.log(_post_id)
        axios.post(edit_post_url, {post_text: app.vue.new_post_text, post_id: _post_id}).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            let res = app.reindex(response.data.posts);
            for (let i of res) {
                console.log(i);
            }
            app.vue.posts = res;
            app.reset_textarea();
        })
    };
    app.copy_posts = (mode) => {
        console.log("got there")
        console.log(app.vue.new_post_text);
        axios.post(copy_posts_url, {post_text: app.vue.new_post_text}).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            console.log("doesnt get here")
            let res = app.reindex(response.data.posts);
            for (let i of res) {
                console.log(i);
            }
            app.vue.posts = res;
            app.reset_textarea();
        })
    };


    app.thumb_cancel = (p_id, p_idx) => {
        console.log("thumbs CANCEL ", p_idx, p_id);
        console.log(app.vue.posts[p_idx].text);
        app.vue.posts[p_idx].thumbs = 0;
        console.log(app.vue.posts[p_idx].thumbs);
        axios.post(thumb_url, {post_id: p_id, rating: 0});
        app.vue.posts[p_idx].expired_likers = true;
    };

    app.thumb_up = (p_id, p_idx) => {
        console.log("thumbs up", p_idx, p_id);
        console.log(app.vue.posts[p_idx].text);
        app.vue.posts[p_idx].thumbs = 1;
        console.log(app.vue.posts[p_idx].thumbs);
        axios.post(thumb_url, {post_id: p_id, rating: 1});
        app.vue.posts[p_idx].expired_likers = true;
    };

    app.thumb_down = (p_id, p_idx) => {
        console.log("thumbs up ", p_idx, p_id);
        console.log(app.vue.posts[p_idx].text);
        app.vue.posts[p_idx].thumbs = -1;
        console.log(app.vue.posts[p_idx].thumbs);
        axios.post(thumb_url, {post_id: p_id, rating: -1});
        app.vue.posts[p_idx].expired_likers = true;
    };

    app.toggle_ppl_who_liked_post = (p_idx, is_show) => {
        console.log("toggling", p_idx, "to", is_show);
        app.vue.posts[p_idx].show_ppl_who_liked_post = is_show;
        console.log("toggled to", app.vue.posts[p_idx].show_ppl_who_liked_post);
    };

    app.get_likers = (p_idx, p_id) => {
        console.log("get_likers");
        if (app.vue.posts[p_idx].expired_likers) {
            axios.get(get_likers_url, {params: {"post_id": p_id}}).then((result) => {
                app.vue.posts[p_idx].likers = result.data;
                app.vue.posts[p_idx].expired_likers = false;
            });
        }
    };

    app.get_haters = (p_idx, p_id) => {
        console.log("get_haters");
        if (app.vue.posts[p_idx].expired_likers) {
            axios.get(get_haters_url, {params: {"post_id": p_id}}).then((result) => {
                app.vue.posts[p_idx].haters = result.data;
            });
        }
    };

    app.delete_post = (_post_id) => {
        axios.post(delete_post_url, {post_id: _post_id}).then(function (response) {
            let res = app.reindex(response.data.posts);
            console.log("ping");
            for (let i of res) {
                console.log(i);
            }
            app.vue.posts = res;
        })
    };
    app.insert_post = (mode) => {
        axios.post(insert_post_url, {post_id: mode}).then(function (response) {
            // response.data contains the response.
            // response has other fields, such as status, etc; see them in the log.
            let res = app.reindex(response.data.posts);
            app.vue.posts = res;
        })
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        reindex: app.reindex,
        change_mode: app.change_mode,
        add_post: app.add_post,
        copy_posts: app.copy_posts,
        delete_post: app.delete_post,
        edit_post: app.edit_post,
        insert_post: app.insert_post,
        reset_textarea: app.reset_textarea,
        thumb_up: app.thumb_up,
        thumb_down: app.thumb_down,
        thumb_cancel: app.thumb_cancel,
        toggle_ppl_who_liked_post: app.toggle_ppl_who_liked_post,
        get_likers: app.get_likers,
        get_haters: app.get_haters,
//      init_posts: app.init_posts
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        console.log("ekans")
        axios.get(get_posts_url).then((result) => {
            let res = app.reindex(result.data.posts);
            console.log("ping");
            for (let i of res) {
                console.log(i);
            }

            app.vue.posts = res;
        })
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

