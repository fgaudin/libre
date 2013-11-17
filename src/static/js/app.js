window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
});

App.ApplicationAdapter = DS.FixtureAdapter.extend();

App.Router.map(function () {
  this.resource('libre', { path: '/' }, function(){
      this.route('login',  { path: 'login' });
      this.resource("friends", { path: "friends" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.resource("public", { path: "public" }, function(){
          this.route('create',  { path: 'new' });
      });
      this.route('create',  { path: '/new' });
      this.resource("message", { path: "/message/:message_id" }, function(){
      });
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

App.Message.FIXTURES = [
   {
     id: 1,
     body: 'Tennessee Pastor Disputes Wildlife Possession Charge by State http://nyti.ms/1eXMq9H ',
     author: 'The New York Times',
     date: new Date('2013-01-01'),
     liked: false
   },
   {
     id: 2,
     body: "Il s'en est passé des choses cette semaine sur @franceinter ! Quoi ?... Réponse sur http://bit.ly/rambo72  #rambobino pic.twitter.com/kxHx4oaOIm",
     author: "France Inter",
     date: new Date('2013-01-01'),
        liked: true
   },
   {
     id: 3,
     body: "Bon, fin de l'analyse politique de comptoir, je vais aller chercher le pain.!",
     author: "Padre Pio",
     date: new Date('2013-01-01'),
     liked: false
   },
   {
     id: 4,
     body: 'Success of Chinese Leader’s Ambitious Economic Plan May Rest on Rural Regions http://nyti.ms/1f0TtOO ',
     author: 'The New York Times',
     date: new Date('2013-06-01'),
     liked: false
   },
   {
     id: 5,
     body: "Catch the last hour of #TEDYouth now -- some exciting speakers coming up! Watch here: http://tedxyouthday.ted.com/",
     author: "Tedx",
     date: new Date('2013-01-01'),
        liked: true
   },
   {
     id: 6,
     body: "Yak shaved: upgraded http://geoportail.renie.fr  to OpenLayers 3 and Angular.js. Much cleaner and more mobile-friendly this way :)",
     author: "Bruno Renié",
     date: new Date('2013-01-01'),
     liked: false
   }
];

App.Feed.FIXTURES = [
    {
        id: "friends",
        messages: [1, 2, 3]
    },
    {
        id: "public",
        messages: [4, 5, 6]
    }
];

App.LibreRoute = Ember.Route.extend({
  model: function () {
      return this.store.find('feed');
  }
});

App.LibreIndexRoute = Ember.Route.extend({
  model: function () {
    return this.modelFor('libre');
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

          var message = this.get('store').createRecord('message', {
              id: Math.floor(Math.random()*100)+7,
              body: body,
              author: 'me',
              date: new Date()
          });
          var feed = this.get('controllers.friendsIndex.content');
          feed.get('messages').addObject(message);

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
