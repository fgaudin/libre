window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
});

//App.ApplicationAdapter = DS.FixtureAdapter.extend();

Ember.Application.initializer({
    name: "socket",
    initialize: function(container, application) {
        var store = container.lookup('store:main');
        store.push('feed', {id: 'friends', messages: []});
        store.push('feed', {id: 'public', messages: []});
        if ("WebSocket" in window) {
            console.log("WebSocket is supported by your Browser!");
            App.ws = new WebSocket("ws://localhost:8888/socket/");
            App.ws.onopen = function() {
                App.ws.send("Message to send");
            };
            App.ws.onmessage = function (evt) {
                var msg = JSON.parse(evt.data);
                if (msg.type == 'feeds') {
                    store.find('feed', 'friends').then(function(feed){
                        msg.data.friends.forEach(function(message){
                            feed.get('messages').addObject(store.push('message', message));
                        });
                    });
                    store.find('feed', 'public').then(function(feed){
                        msg.data.public.forEach(function(message){
                            feed.get('messages').addObject(store.push('message', message));
                        });
                    });
                }
            };
            App.ws.onclose = function() {
                console.log("Connection closed");
            };
        } else {
            console.log("Websocket not supported");
        }
    }
});

App.Router.map(function () {
  this.resource('libre', { path: '/' }, function(){
      this.route('login',  { path: 'login' });
      this.resource("friends", { path: "friends" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.resource("public", { path: "public" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.resource("message", { path: "/message/:message_id" });
  });
});

App.Feed = DS.Model.extend({
    messages: DS.hasMany('message', {async:true})
});

App.Message = DS.Model.extend({
  body: DS.attr('string'),
  author: DS.attr('string'),
  date: DS.attr('date'),
  liked: DS.attr('boolean'),

  feed: DS.belongsTo('feed'),

  formatedDate: function() {
    return this.get('date').toLocaleString();
  }.property('date')
});

App.LibreIndexRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('feed');
    }
});

App.LibreIndexController = Ember.ArrayController.extend({
    friends: function(){
        return this.store.find('feed', 'friends');
    }.property(),
    public: function(){
        return this.store.find('feed', 'public');
    }.property()
});

App.LibreLoginRoute = Ember.Route.extend({
    beforeModel: function() {
        var route = this;
        App.$.post( "/login", function(data){
            route.transitionTo('libre');
        });
    }
});

App.FriendsIndexRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('feed', "friends");
    }
});

App.PublicIndexRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('feed', "public");
    }
});

App.FriendCreateController = Ember.Controller.extend({
    needs: ['friendsIndex'],
    actions: {
        create: function () {
          var body = this.get('newMessage');
          if (!body.trim()) { return; }

          var payload = {
              type:'friend_message',
          };
          var message = this.get('store').createRecord('message', {
              body: body,
              author: 'me',
              date: new Date()
          });
          var feed = this.get('controllers.friendsIndex.content');
          feed.get('messages').addObject(message);

          message.save();

          this.set('newMessage', '');
        }
    }
});

App.PublicCreateController = Ember.Controller.extend({
    needs: ['publicIndex'],
    actions: {
        create: function () {
            var body = this.get('newMessage');
            if (!body.trim()) { return; }

            var message = this.get('store').createRecord('message', {
                id: Math.floor(Math.random()*100)+7,
                body: body,
                author: 'me',
                date: new Date()
            });
            var feed = this.get('controllers.publicIndex.content');
            feed.get('messages').addObject(message);

            this.set('newMessage', '');
        }
    }
});

App.MessageController = Ember.ObjectController.extend({
    actions: {
        toggleLike: function(message_id){
            this.store.find('message', message_id).then(function(message){
                var value = !message.get('liked');
                message.set('liked', value);
            });
        }
    }
});
