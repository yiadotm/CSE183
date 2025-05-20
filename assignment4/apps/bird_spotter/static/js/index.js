"use strict";
function clone(obj) { return JSON.parse(JSON.stringify(obj)); }

let app = {}
app.empty_new_bird = {"id": 0, "name": "", "habitat": "", "weight": 0, "sightings": 0},
app.config = {
    data: function() {
        return {
            new_bird: clone(app.empty_new_bird),            
            birds: [],
            selected_birds: [],
            editing: {current: null},
            // componentKey: 0,
            errorMessage: "",
        };
    },
    methods: {       

        search: function() {
            this.cancel();
            this.selected_birds = this.birds.filter((bird)=>{return bird.name.toLowerCase().includes(this.new_bird.name.toLowerCase()); });
            
        },
        add_bird: function() {
            this.cancel();
            if (this.selected_birds.length==0 && this.new_bird.name.length>1) {
                if (this.new_bird.weight < 0 || this.new_bird.weight > 1000) {
                    this.errorMessage = 'Weight must be between 0 and 1000';
                    return;
                }
                let bird = clone(this.new_bird);
                this.birds.push(bird);
                this.new_bird = app.empty_new_bird;
                this.selected_birds = [bird];
                let birdData = {
                    name: bird.name,
                    habitat: bird.habitat,
                    weight: bird.weight,
                    sightings: bird.sightings
                };
                
                // POST bird to /bird_spotter/birds which returns {id: #} and store it in bird.id = #;
                console.log('Bird to send:', bird);
                axios.post("/bird_spotter/api/birds", birdData)
                .then((res) => {  
                    bird.id = res.data.id;
                    app.load_data();
                    console.log('Updated bird:', bird);
                    console.log('Updated selected_bird:', this.selected_birds);  
                })
                .catch(function(error) {
                    console.log(error);
                });
        
                // remove the following
                // bird.id = (new Date()).getTime();
            }            
        },
        edit: function(bird) {
            this.cancel();
            this.editing = {current: bird, old: clone(bird)};
        },
        save: function(bird) {
            let birdId = bird.id;  
            if (bird.weight < 0 || bird.weight > 1000) {
                this.errorMessage = 'Weight cannot be negative';
                return;
            }
            bird = clone(bird);            
            // delete bird.id;
            // delete bird.name;
            // PUT bird to /bird_spotter/birds/{bird.id}       
            axios.put(`/bird_spotter/api/birds/${birdId}`, bird)
            .then(function(res){
                if (res.data.updated) {
                    console.log("Update successful");
                    Object.assign(this.editing.current, bird);
                    app.load_data();
                } else {
                    console.log("Update failed", res.data.errors);
                }
            })
            .catch(function(error) {
                console.log(error);
            });
        
            this.editing = {current: null};
        },
        cancel: function() {
            if (this.editing.current)
                for(var key in this.editing.current)
                    this.editing.current[key] = this.editing.old[key];
            this.editing = {current: null};
        },
        add_sighting: function(bird) {
            axios.post(`/bird_spotter/api/birds/${bird.id}/increase_sightings`, {})
                .then(function(res){
                    console.log(res.data);
                    if (res.data.success && res.data.updated) {
                        bird.sightings += 1;
                        app.load_data();
                    } else if (res.data.errors) {
                        console.log('Error:', res.data.errors);
                    }
                })
                .catch(function(error) {
                    console.log(error);
                });
        },
        color: function(name) {            
            let hash = 0;
            for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);            
            let ret = `hsl(${(hash % 360)}, 100%, 75%)`;                         
            console.log(ret);
            return ret;
        },
    }
};
app.load_data = function() {
    // GET from /bird_spotter/birds {birds: [...]} and store it into app.vue.birds = [...]
    axios.get("/bird_spotter/api/birds").then(function(res){
        app.vue.birds = res.data.birds;
        app.vue.selected_birds = res.data.birds;
        // app.vue.componentKey += 1;
    })
    .catch((error) => {
        const response = error.response
        console.log(response.data.errors)
    });
}
app.vue = Vue.createApp(app.config).mount("#app");
app.load_data();