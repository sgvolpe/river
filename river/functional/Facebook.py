import facebook
def main():
    # Fill in the values noted in previous steps here
    cfg = {
        "page_id": "10156973440365966",  # Step 1
        "access_token": "EAAHoT7BxOjUBAKTVZAhiL4xqM0reZACyDpLfeCvMdd4dTKA3gMOLHI5zpZCDKN42cRtwOrR3nfKMt9ILuquZBll9hTaprdQMrZBThzlmNqSqCdmaPJJO82t0K1bh7ZBs3ZBaqAFmTGYRZBpUXqNnubUMH6tzhWWCQrbUwxU60xbOpLicYaGFTfvBu1UCSxxbxiJOR5vazYtrYtuYZCOxfYyjqkvOWmc625klipv5selGhIQZDZD"
        # Step 3
    }
    api = get_api(cfg)
    msg = "Hello, world!"
    status = api.put_wall_post(msg)
def get_api(cfg):
    graph = facebook.GraphAPI(access_token=cfg['access_token'], version="2.7")
    resp = graph.get_object('me/accounts')
    print(resp)
    page_access_token = None
    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
        graph = facebook.GraphAPI(page_access_token)
        return graph


def facebook_post():
    import facebook

    def get_token():
        return 'EAAHoT7BxOjUBAIRDoYlT9SIZBxiZAYqeXxa5BfjLTEWa1CADPZC5mJyBPKZCN3NSIjFDrtaZAkZBbKV0tByEpFZATYqeQXBcYrZAMyHplRDpZCF4VkaIAnQDeNd48Gs2EzASvMNfzMzfsJvXCmWMHZA2aJsln8f3rZCZBgEkBmZAbMn5FKFY2XxyHojUHyvXw0GUtDbyfa6hcLlN2G5gBdxKCFQQRpzZC4Oucmh479iP4tvt5KZCwZDZD'

    host = 'graph.facebook.com'

    graph = facebook.GraphAPI(access_token=get_token(), version="7.0")

    print(graph.get_object(id='10156973440365966', fields='photos'))
    print(graph.get_object(id='2304301603151927', fields='photos'))

    """graph.put_object(
        parent_object="me",
        connection_name="feed",
        message="This is a great website. Everyone should visit it.",
    #    link="https://www.facebook.com"
    )"""
