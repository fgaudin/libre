window.App = Ember.Application.create({
    LOG_TRANSITIONS: true,
    LOG_TRANSITIONS_INTERNAL: true
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
            App.ws = new WebSocket("ws://" + window.location.host + "/socket");
            App.ws.onopen = function() {
                App.ws.send("Message to send");
            };
            App.ws.onmessage = function (evt) {
                console.log('received: ' + evt.data)
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
      this.resource("user", { path: "user" }, function(){
          this.resource("user_friends", { path: "friends" }),
          this.resource("user_public", { path: "public" })
      });
      this.resource("friends", { path: "friends" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.resource("public", { path: "public" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.resource("message", { path: "/message/:message_id" });
  });
});

App.User = DS.Model.extend({

});

App.Message = DS.Model.extend({
  body: DS.attr('string'),
  author_username: DS.attr('string'),
  author_fullname: DS.attr('string'),
  date: DS.attr('date'),
  likes: DS.attr('number'),
  liked: DS.attr('boolean'),
  scope: DS.attr('string'),

  formatedDate: function() {
      if (this.get('date')) {
          return this.get('date').toLocaleString();
      }
      return '';
  }.property('date')
});

App.LibreController = Ember.Controller.extend({
    authenticated: false,
    actions: {
       login: function(){
           var email = this.get('email');
           var password = this.get('password');
           var ctrl = this;
           App.$.post( "/login",
           {email: email, password: password},
           function(data) {
               console.log(data);
               if (data.authenticated) {
                   ctrl.set('email', '');
                   ctrl.set('password', '');
                   ctrl.set('authenticated', true);
               }
           },
           'json');
        }
    }
});

App.LibreRoute = Ember.Route.extend({
    model: function(){
        return this.store.find('message');
    }
});

App.LibreIndexRoute = Ember.Route.extend({
    model: function(){
        return this.modelFor('libre');
    }
});

App.LibreIndexController = Ember.ArrayController.extend({
    sortProperties: ['id'],
    sortAscending: false,
    friends: function(){
        return this.filterBy('scope', 'friends');
    }.property(),
    public: function(){
        return this.filterBy('scope', 'public');
    }.property()
});

App.FriendsIndexRoute = Ember.Route.extend({
    model: function () {
        return this.modelFor('libre').filterBy('scope', 'friends');
    }
});

App.FriendsIndexController = Ember.ArrayController.extend({
    sortProperties: ['id'],
    sortAscending: false
});

App.PublicIndexRoute = Ember.Route.extend({
    model: function () {
        return this.modelFor('libre').filterBy('scope', 'public');
    }
});

App.PublicIndexController = Ember.ArrayController.extend({
    sortProperties: ['id'],
    sortAscending: false
});

App.LibreLoginRoute = Ember.Route.extend({
    beforeModel: function() {
        var route = this;
        App.$.post( "/login", function(data){
            route.transitionTo('libre');
        });
    }
});

App.UserFeedController = Ember.Controller.extend({
    friends: function(){
        return this.store.find('friendMessage');
    }.property(),
    public: function(){
        return this.store.find('publicMessage');
    }.property()
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
