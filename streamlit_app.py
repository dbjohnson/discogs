import discogs_client
import pandas as pd
import seaborn as sns


DISCOGS_TOKEN = 'xeRXlxQaOkLoGprJgqzHtpvipJWPoOcvwSiyfHvo'


dir(client.user(user))


r = all_releases[1]

r.data['basic_information']['year']
m = r.release.master
dir(m)
m.data
x = m.main_release
x.data

dir(r.release)



def release_data(user='d.bryan.johnson'):
    """
    Super annoying, but getting to the master release for each item
    is a separate query, and requests are rate limited to 60 per min :/
    This means that we can't easily get the original year of release
    """
    client = discogs_client.Client(
        'my_user_agent/1.0',
        user_token=DISCOGS_TOKEN
    )

    all_releases = [
        item
        for folder in client.user(user).collection_folders
        for item in folder.releases
    ]

    df_releases = pd.DataFrame([{
        'artist': data['artists'][0]['name'],
        'label': data['labels'][0]['name'],
        'genre': data['genres'][0],
        **{
            k: data[k]
            for k in (
                'title', 'master_url', 'master_id', 'cover_image',
                'rating', 'date_added', 'rating', 'id', 'year'
            )
        },
    }
        for item in all_releases
        for data in [{
            **item.data,
            **item.data['basic_information']
        }]
    ]).drop_duplicates()

    df_releases = df_releases.assign(
        decade=(df_releases['year'] // 10) * 10
    )
    return df_releases

    df_artists = pd.DataFrame([{
        'release_id': item.release.id,
        **a,
    }
        for item in all_releases
        for a in item.release.data.get(
            'extraartists',
            item.release.data['artists']
    )]).drop_duplicates()

    return df_releases, df_artists


df_releases = release_data()

df_releases.sort_values(by='date_added').tail()

for k in ('artist', 'genre', 'label'):
    counts = df_releases[k].value_counts().reset_index()
    genre = df_releases[k].value_counts().reset_index()
    fig = sns.mpl.pyplot.figure(figsize=(8, len(counts) // 3))
    sns.barplot(
        x=k,
        y='index',
        data=counts,
        color='b'
    )
    fig.gca().set_title(k)
    fig.gca().set_xlabel('')
    fig.gca().set_ylabel('')
    st.pyplot(fig)
