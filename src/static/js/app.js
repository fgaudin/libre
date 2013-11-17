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
      this.route('create',  { path: '/new' });
      this.resource("message", { path: "/message/:message_id" }, function(){
      });
  });
});

App.Message = DS.Model.extend({
  body: DS.attr('string'),
  author: DS.attr('string'),
  date: DS.attr('date'),
  liked: DS.attr('boolean'),

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

App.FriendFeed = DS.Model.extend({
    messages: DS.hasMany('message', { async: true })
});

App.PublicFeed = DS.Model.extend({
    messages: DS.hasMany('message', { async: true })
});

App.ApplicationRoute = Ember.Route.extend({
    model: function() {
      var store = this.get('store');

      store.push('friendFeed', {
          id: 1,
          messages: [1, 2, 3]
      });
    }
  });

App.LibreRoute = Ember.Route.extend({
  model: function () {
      return this.modelFor('friends');
  }
});

App.LibreIndexRoute = Ember.Route.extend({
  model: function () {
    return this.modelFor('friends');
  }
});

App.FriendsIndexRoute = Ember.Route.extend({
    model: function () {
        return this.store.find('friendFeed', 1);
    }
});

App.FriendCreateController = Ember.Controller.extend({
    actions: {
        create: function () {
          var body = this.get('newMessage');
          if (!body.trim()) { return; }

          var message = this.get('store').createRecord('message', {
            id: 7,
            body: body,
            author: 'me',
            date: new Date()
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
