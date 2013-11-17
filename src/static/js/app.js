window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
});

//App.ApplicationAdapter = DS.FixtureAdapter.extend();

Ember.Application.initializer({
    name: "socket",
    initialize: function(container, application) {
        var store = container.lookup('store:main');
        //store.push('feed', {id: 'friends', messages: []});
        //store.push('feed', {id: 'public', messages: []});
        if ("WebSocket" in window) {
            console.log("WebSocket is supported by your Browser!");
            App.ws = new WebSocket("ws://localhost:8888/socket");
            App.ws.onopen = function() {
                App.ws.send("Message to send");
            };
            App.ws.onmessage = function (evt) {
                var msg = JSON.parse(evt.data);
                if (msg.type == 'message') {
                    store.push('message', msg.data);
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

App.Message = DS.Model.extend({
  body: DS.attr('string'),
  author: DS.attr('string'),
  date: DS.attr('date'),
  likes: DS.attr('number'),
  liked: DS.attr('boolean'),
  scope: DS.attr('string'),
  //scope: DS.belongsTo('feed'),

  formatedDate: function() {
      if (this.get('date')) {
          return this.get('date').toLocaleString();
      }
      return '';
  }.property('date')
});

//App.FriendMessage = App.Message.extend();
//App.PublicMessage = App.Message.extend();

App.LibreIndexController = Ember.ArrayController.extend({
    friends: function(){
        return this.store.find('message', {scope: 'friends'});
    }.property(),
    public: function(){
        return this.store.find('message', {scope: 'public'});
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
        return this.store.find('message', {scope: 'friends'});
    }
});

App.PublicIndexRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('message', {scope: 'public'});
    }
});

App.FriendCreateController = Ember.Controller.extend({
    actions: {
        create: function () {
          var body = this.get('newMessage');
          if (!body.trim()) { return; }

          var message = this.get('store').createRecord('message', {
              body: body,
              scope: 'friends'
          });
          message.save();

          this.set('newMessage', '');
        }
    }
});

App.PublicCreateController = Ember.Controller.extend({
    actions: {
        create: function () {
            var body = this.get('newMessage');
            if (!body.trim()) { return; }

            var message = this.get('store').createRecord('message', {
                body: body,
                scope: 'public'
            });
            message.save();

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
