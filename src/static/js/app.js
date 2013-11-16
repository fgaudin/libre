window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
});

App.ApplicationAdapter = DS.FixtureAdapter.extend();

App.Router.map(function () {
  this.resource('libre', { path: '/' }, function(){
      this.route('login',  { path: '/login' });
      this.resource("message", { path: "/message/:message_id" }, function(){
      this.route('create',  { path: '/message/new' });
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
   }
  ];

App.LibreRoute = Ember.Route.extend({
  model: function () {
    return this.store.find('message');
  }
});

App.LibreIndexRoute = Ember.Route.extend({
  model: function () {
    return this.modelFor('libre');
  }
});

App.LibreIndexController = Ember.ArrayController.extend({
    sortProperties: ['id'],
    sortAscending: false,
    actions: {
        toggleLike: function(message_id){
        this.store.find('message', message_id).then(function(message){
                var value = !message.get('liked');
                message.set('liked', value);
            });
        }
    }
});

App.MessageCreateController = Ember.ObjectController.extend({
    actions: {
        create: function () {
          var body = this.get('newMessage');
          if (!body.trim()) { return; }

          var message = this.get('store').createRecord('message', {
            id: 4,
            body: body,
            author: 'me',
            date: new Date()
          });
          this.set('newMessage', '');
        }
    }
});
