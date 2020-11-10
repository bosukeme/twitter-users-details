from flask_restful import Resource
import twitter_users_info


class Twitter(Resource):   

    def get(self):
        
        
        result=twitter_users_info.run_all()

        return ('Process Complete')
        


