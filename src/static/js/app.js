window.App = Ember.Application.create({
    LOG_TRANSITIONS: true,
    LOG_TRANSITIONS_INTERNAL: true,
    openSocket: function(store){
        if ("WebSocket" in window) {
            console.log("WebSocket is supported by your Browser!");
            App.ws = new WebSocket("ws://" + window.location.host + "/socket");
            App.ws.onopen = function() {
            };
            App.ws.onmessage = function (evt) {
                console.log('received: ' + evt.data)
                var msg = JSON.parse(evt.data);
                if (msg.type == 'message') {
                    msg.data.forEach(function(message){
                        store.push('message', message);
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
      this.resource("user", { path: "user" }, function(){
          this.resource('user_profile',  { path: ':username' }, function(){
              this.resource("user_friends", { path: "friends" }),
              this.resource("user_public", { path: "public" })
          });
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
    username: DS.attr('string'),
    fullname: DS.attr('string'),
    pic: DS.attr('string'),
    friend: DS.attr('boolean'),
    friend_requested: DS.attr('boolean'),
    friend_waiting: DS.attr('boolean'),
    followed: DS.attr('boolean'),

    friends: DS.attr('number'),
    followers: DS.attr('number'),
    following: DS.attr('number'),
    messages: DS.attr('number'),

    friend_state: function(){
        if (this.get('friend')) {
            return 'Friends';
        } else if (this.get('friend_requested')) {
            return 'Requested';
        } else if (this.get('friend_waiting')) {
            return 'Accept request';
        } else {
            return 'Add';
        }
    }.property('friend', 'friend_requested', 'friend_waiting')
});

App.Message = DS.Model.extend({
  body: DS.attr('string'),
  author_username: DS.attr('string'),
  author_fullname: DS.attr('string'),
  author_pic: DS.attr('string'),
  date: DS.attr('date'),
  like_count: DS.attr('number'),
  liked: DS.attr('boolean'),
  comment_count: DS.attr('number'),
  scope: DS.attr('string'),
  forMe: DS.attr('boolean'),

  url: DS.attr('string'),
  title: DS.attr('string'),
  pic: DS.attr('string'),
  width: DS.attr('number'),
  height: DS.attr('number'),

  comments: function(){
      var msg_id = this.get('id');
      result = this.get('store').filter('comment', function(comment){
          return comment.get('msg_id') == msg_id;
      });
      return result;
  }.property(),
  getComments: function(){
      var msg_id = this.get('id');
      this.get('store').find('comment', {message_id: msg_id});
  },

  numericId: function(){
      return parseInt(this.get('id'), 10);
  }.property('id'),
  formatedDate: function() {
      if (this.get('date')) {
          return this.get('date').toLocaleString();
      }
      return '';
  }.property('date')
});

App.Comment = DS.Model.extend({
    content: DS.attr('string'),
    author_username: DS.attr('string'),
    author_fullname: DS.attr('string'),
    author_pic: DS.attr('string'),
    msg_id: DS.attr('number')
});

App.LibreController = Ember.Controller.extend({
    authenticated: false,
    actions: {
        logout: function(){
            var ctrl = this;
            App.$.post( "/logout",
            function(data) {
                if (!data.authenticated) {
                    ctrl.set('authenticated', false);
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
    needs: "libre",
    libre: Ember.computed.alias("controllers.libre"),
    sortProperties: ['numericId'],
    sortAscending: false,
    friends: function(){
        return this.filterBy('scope', 'friends').filterBy('forMe', true);
    }.property('model.@each'),
    public: function(){
        return this.filterBy('scope', 'public').filterBy('forMe', true);
    }.property('model.@each'),
    actions: {
        emailSignup: function(){
            var email = this.get('email');
            var password = this.get('password');
            var ctrl = this;
            App.$.post( "/signup",
            {email: email, password: password},
            function(data) {
                console.log(data);
                if (data.authenticated) {
                    ctrl.set('email', '');
                    ctrl.set('password', '');
                    ctrl.get('libre').set('authenticated', true);
                } else {
                    console.log('signup failed');
                }
            },
            'json');
        },
        emailLogin: function(){
            var email = this.get('email');
            var password = this.get('password');
            var action = this;
            var ctrl = this;
            App.$.post( "/login/email",
            {email: email, password: password},
            function(data) {
                console.log(data);
                if (data.authenticated) {
                    ctrl.set('email', '');
                    ctrl.set('password', '');
                    ctrl.get('libre').set('authenticated', true);
                    App.openSocket(ctrl.get('store'))
                }
            },
            'json');
         },
         facebookLogin: function(){
             window.open("/login/facebook", "_blank", "height=400,width=600");
         },
         googleLogin: function(){
             window.open("/login/google", "_blank", "height=400,width=600");
         },
         twitterLogin: function(){
             window.open("/login/twitter", "_blank", "height=400,width=600");
         }
    }
});

App.MessageTplComponent = Ember.Component.extend({
    commentsShown: false,
    actions: {
        like: function(message){
            var value = !message.get('liked');
            message.set('liked', value);
            if (value) {
                message.incrementProperty('like_count');
            } else {
                message.decrementProperty('like_count');
            }
            App.$.post('/like', {
                message_id: message.id
            }, function(response){
            }, 'json');
        },
        showComments: function(message){
            message.getComments();
            this.set('commentsShown', true);
        },
        comment: function(message){
            var comment = this.get('newComment');
            var comp = this;
            App.$.post('/comments', {
                message_id: message.id,
                comment: comment
            }, function(response){
                comp.set('newComment', '');
            }, 'json');
        }
    }
});

App.UserProfileRoute = Ember.Route.extend({
    model: function (params) {
        console.log(params.username);
        this.set('username', params.username);
        return this.modelFor('libre');
    },
    setupController: function(controller, model) {
        this._super(controller, model);
        this.controllerFor('userProfileIndex').set('username', this.get('username'));
        this.controllerFor('userProfileIndex').set('model', model);
    }
});

App.UserProfileIndexController = Ember.ArrayController.extend({
    sortProperties: ['numericId'],
    sortAscending: false,
    author: function(){
        var username = this.get('username');
        console.log('author: ' + username);
        return this.get('store').find('user', username);
    }.property('username'),
    friends: function(){
        console.log("-> " + this.get('username'));
        return this.filterBy('scope', 'friends').filterBy('author_username', this.get('username'));
    }.property('model.@each', 'username'),
    public: function(){
        //return this.filterBy('scope', 'public').filterBy('author_username', this.get('username'));
        return this.get('store').find('message', {username: this.get('username')});
    }.property('model.@each', 'username'),
    actions: {
        toggle_friend: function(){
            var url = '/users/' + this.get('username');
            var user = this.get('author');
            var controller = this;
            if (user.get('friend')) {
                if (this.get('unfriending')) {
                    App.$.post(url, {
                        action: 'unfriend'
                    }, function(response){
                        if (response) {
                            user.set('friend', response.friend)
                            controller.set('unfriending', false);
                        }
                    }, 'json');
                } else {
                    this.set('unfriending', true);
                }
            } else  if (user.get('friend_requested')){
                App.$.post(url, {
                    action: 'cancel_friend_request'
                }, function(response){
                    if (response) {
                        user.set('friend_requested', response.friend_requested)
                    }
                }, 'json');
            } else if (user.get('friend_waiting')){
                App.$.post(url, {
                    action: 'accept_friend'
                }, function(response){
                    if (response) {
                        user.set('friend', response.friend)
                    }
                }, 'json');
            } else {
                App.$.post(url, {
                    action: 'request_friend'
                }, function(response){
                    if (response) {
                        user.set('friend_requested', response.friend_requested)
                    }
                }, 'json');
            }
        },
        toggle_follow: function(){
            var url = '/users/' + this.get('username');
            var user = this.get('author');
            var action = 'follow';
            if (user.get('followed')) {
                action = 'unfollow';
            }
            App.$.post(url, {
                action: action
            }, function(response){
                if (response) {
                    user.set('followed', response.followed)
                }
            }, 'json');
        }
    }
});

App.FriendCreateController = Ember.Controller.extend({
    actions: {
        create: function () {
          var body = this.get('newMessage');
          if (!body.trim()) { return; }

          var message = App.$.post('/messages', {
              body: body,
              scope: 'friends'
          });

          this.set('newMessage', '');
        }
    }
});

App.PublicCreateController = Ember.Controller.extend({
    actions: {
        create: function () {
            var body = this.get('newMessage');
            if (!body.trim()) { return; }

            var message = App.$.post('/messages', {
                body: body,
                scope: 'public'
            });

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
