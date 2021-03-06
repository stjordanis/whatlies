from typing import Union
from copy import deepcopy
from functools import reduce

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import altair as alt
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import paired_distances

from whatlies.embedding import Embedding
from whatlies.common import plot_graph_layout


class EmbeddingSet:
    """
    This object represents a set of `Embedding`s. You can use the same operations
    as an `Embedding` but here we apply it to the entire set instead of a single
    `Embedding`.

    **Parameters**

    - **embeddings**: list of embeddings or dictionary with name: embedding.md pairs
    - **name**: custom name of embeddingset

    Usage:

    ```python
    from whatlies.embedding import Embedding
    from whatlies.embeddingset import EmbeddingSet

    foo = Embedding("foo", [0.1, 0.3])
    bar = Embedding("bar", [0.7, 0.2])
    emb = EmbeddingSet(foo, bar)
    emb = EmbeddingSet({'foo': foo, 'bar': bar)
    ```
    """

    def __init__(self, *embeddings, name=None):
        if not name:
            name = "Emb"
        self.name = name
        if len(embeddings) == 1:
            # we assume it is a dictionary here
            self.embeddings = embeddings[0]
        else:
            # we assume it is a tuple of tokens
            self.embeddings = {t.name: t for t in embeddings}

    def __contains__(self, item):
        """
        Checks if an item is in the embeddingset.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        "foo" in emb # True
        "dinosaur" in emb # False
        ```
        """
        return item in self.embeddings.keys()

    def __iter__(self):
        """
        Iterate over all the embeddings in the embeddingset.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        [e for e in emb]
        ```
        """
        return self.embeddings.values().__iter__()

    def __add__(self, other):
        """
        Adds an embedding to each element in the embeddingset.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        (emb).plot(kind="arrow")
        (emb + buz).plot(kind="arrow")
        ```
        """
        new_embeddings = {k: emb + other for k, emb in self.embeddings.items()}
        return EmbeddingSet(new_embeddings, name=f"({self.name} + {other.name})")

    def __sub__(self, other):
        """
        Subtracts an embedding from each element in the embeddingset.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        (emb).plot(kind="arrow")
        (emb - buz).plot(kind="arrow")
        ```
        """
        new_embeddings = {k: emb - other for k, emb in self.embeddings.items()}
        return EmbeddingSet(new_embeddings, name=f"({self.name} - {other.name})")

    def __or__(self, other):
        """
        Makes every element in the embeddingset othogonal to the passed embedding.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        (emb).plot(kind="arrow")
        (emb | buz).plot(kind="arrow")
        ```
        """
        new_embeddings = {k: emb | other for k, emb in self.embeddings.items()}
        return EmbeddingSet(new_embeddings, name=f"({self.name} | {other.name})")

    def __rshift__(self, other):
        """
        Maps every embedding in the embedding set unto the passed embedding.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar)

        (emb).plot(kind="arrow")
        (emb >> buz).plot(kind="arrow")
        ```
        """
        new_embeddings = {k: emb >> other for k, emb in self.embeddings.items()}
        return EmbeddingSet(new_embeddings, name=f"({self.name} >> {other.name})")

    def compare_against(self, other, mapping="direct"):
        if mapping == "direct":
            return [v > other for k, v in self.embeddings.items()]

    def to_X(self):
        """
        Takes every vector in each embedding and turns it into a scikit-learn compatible `X` matrix.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        emb = EmbeddingSet(foo, bar, buz)

        X = emb.to_X()
        ```
        """
        X = np.array([i.vector for i in self.embeddings.values()])
        return X

    def to_X_y(self, y_label):
        """
        Takes every vector in each embedding and turns it into a scikit-learn compatible `X` matrix.
        Also retreives an array with potential labels.

        Usage:

        ```python
        from whatlies.embedding import Embedding
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3])
        bar = Embedding("bar", [0.7, 0.2])
        buz = Embedding("buz", [0.1, 0.9])
        bla = Embedding("bla", [0.2, 0.8])

        emb1 = EmbeddingSet(foo, bar).add_property("label", lambda d: 'group-one')
        emb2 = EmbeddingSet(buz, bla).add_property("label", lambda d: 'group-two')
        emb = emb1.merge(emb2)

        X, y = emb.to_X_y(y_label='label')
        ```
        """
        X = self.to_X()
        y = np.array([getattr(e, y_label) for e in self.embeddings.values()])
        return X, y

    def transform(self, transformer):
        """
        Applies a transformation on the entire set.

        Usage:

        ```python
        from whatlies.embeddingset import EmbeddingSet
        from whatlies.transformers import Pca

        foo = Embedding("foo", [0.1, 0.3, 0.10])
        bar = Embedding("bar", [0.7, 0.2, 0.11])
        buz = Embedding("buz", [0.1, 0.9, 0.12])
        emb = EmbeddingSet(foo, bar, buz).transform(Pca(2))
        ```
        """
        return transformer(self)

    def __getitem__(self, thing):
        """
        Retreive a single embedding from the embeddingset.

        Usage:
        ```python
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3, 0.10])
        bar = Embedding("bar", [0.7, 0.2, 0.11])
        buz = Embedding("buz", [0.1, 0.9, 0.12])
        emb = EmbeddingSet(foo, bar, buz)

        emb["buz"]
        ```
        """
        if isinstance(thing, str):
            return self.embeddings[thing]
        new_embeddings = {t: self[t] for t in thing}
        names = ",".join(thing)
        return EmbeddingSet(new_embeddings, name=f"{self.name}.subset({names})")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.embeddings.keys())

    def filter(self, func):
        """
        Filters the collection of embeddings based on a predicate function.

        Arguments:
             func: callable that accepts a single embedding and outputs a boolean

        ```python
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3, 0.10])
        bar = Embedding("bar", [0.7, 0.2, 0.11])
        buz = Embedding("buz", [0.1, 0.9, 0.12])
        xyz = Embedding("xyz", [0.1, 0.9, 0.12])
        emb = EmbeddingSet(foo, bar, buz, xyz)
        emb.filter(lambda e: "foo" not in e.name)
        ```
        """
        return EmbeddingSet({k: v for k, v in self.embeddings.items() if func(v)})

    def merge(self, other):
        """
        Concatenates two embeddingssets together

        Arguments:
            other: another embeddingset

        Usage:

        ```python
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3, 0.10])
        bar = Embedding("bar", [0.7, 0.2, 0.11])
        buz = Embedding("buz", [0.1, 0.9, 0.12])
        xyz = Embedding("xyz", [0.1, 0.9, 0.12])
        emb1 = EmbeddingSet(foo, bar)
        emb2 = EmbeddingSet(xyz, buz)

        both = em1.merge(emb2)
        ```
        """
        return EmbeddingSet({**self.embeddings, **other.embeddings})

    def add_property(self, name, func):
        """
        Adds a property to every embedding in the set. Very useful for plotting because
        a property can be used to assign colors.

        Arguments:
            name: name of the property to add
            func: function that receives an embedding and needs to output the property value

        Usage:

        ```python
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [0.1, 0.3, 0.10])
        bar = Embedding("bar", [0.7, 0.2, 0.11])
        emb = EmbeddingSet(foo, bar)
        emb_with_property = emb.add_property('example', lambda d: 'group-one')
        ```
        """
        return EmbeddingSet(
            {k: e.add_property(name, func) for k, e in self.embeddings.items()}
        )

    def average(self, name=None):
        """
        Takes the average over all the embedding vectors in the embeddingset. Turns it into
        a new `Embedding`.

        Arguments:
            name: manually specify the name of the average embedding

        Usage:

        ```python
        from whatlies.embeddingset import EmbeddingSet

        foo = Embedding("foo", [1.0, 0.0])
        bar = Embedding("bar", [0.0, 1.0])
        emb = EmbeddingSet(foo, bar)

        emb.average().vector                   # [0.5, 0,5]
        emb.average(name="the-average").vector # [0.5, 0.5]
        ```
        """
        name = f"{self.name}.average()" if not name else name
        x = self.to_X()
        return Embedding(name, np.mean(x, axis=0))

    def embset_similar(self, emb: Union[str, Embedding], n: int = 10, metric="cosine"):
        """
        Retreive an [EmbeddingSet][whatlies.embeddingset.EmbeddingSet] that are the most simmilar to the passed query.

        Arguments:
            emb: query to use
            n: the number of items you'd like to see returned
            metric: metric to use to calculate distance, must be scipy or sklearn compatible

        Returns:
            An [EmbeddingSet][whatlies.embeddingset.EmbeddingSet] containing the similar embeddings.
        """
        embs = [w[0] for w in self.score_similar(emb, n, metric)]
        return EmbeddingSet({w.name: w for w in embs})

    def score_similar(self, emb: Union[str, Embedding], n: int = 10, metric="cosine"):
        """
        Retreive a list of (Embedding, score) tuples that are the most similar to the passed query.

        Arguments:
            emb: query to use
            n: the number of items you'd like to see returned
            metric: metric to use to calculate distance, must be scipy or sklearn compatible

        Returns:
            An list of ([Embedding][whatlies.embedding.Embedding], score) tuples.
        """
        if n > len(self):
            raise ValueError(
                f"You cannot retreive (n={n}) more items than exist in the Embeddingset (len={len(self)})"
            )

        if isinstance(emb, str):
            if emb not in self.embeddings.keys():
                raise ValueError(
                    f"Embedding for `{emb}` does not exist in this EmbeddingSet"
                )
            emb = self[emb]

        vec = emb.vector
        queries = [w for w in self.embeddings.keys()]
        vector_matrix = self.to_X()
        distances = pairwise_distances(vector_matrix, vec.reshape(1, -1), metric=metric)
        by_similarity = sorted(zip(queries, distances), key=lambda z: z[1])
        return [(self[q], float(d)) for q, d in by_similarity[:n]]

    def to_matrix(self):
        """
        Does exactly the same as `.to_X`. It takes the embedding vectors and turns it into a numpy array.
        """
        return self.to_X()

    def to_dataframe(self):
        """
        Turns the embeddingset into a pandas dataframe.
        """
        mat = self.to_matrix()
        return pd.DataFrame(mat, index=list(self.embeddings.keys()))

    def movement_df(self, other, metric="euclidean"):
        """
        Creates a dataframe that shows the movement from one embeddingset to another one.

        Arguments:
            other: the other embeddingset to compare against, will only keep the overlap
            metric: metric to use to calculate movement, must be scipy or sklearn compatible

        Usage:

        ```python
        from whatlies.language import SpacyLanguage
        lang1 = SpacyLanguage("en_core_web_sm")
        lang2 = SpacyLanguage("en_core_web_md")

        names = ['red', 'blue', 'green', 'yellow', 'cat', 'dog', 'mouse', 'rat', 'bike', 'car']
        emb1 = lang1[names]
        emb2 = lang2[names]
        emb1.movement_df(emb2)
        ```
        """
        overlap = list(
            set(self.embeddings.keys()).intersection(set(other.embeddings.keys()))
        )
        mat1 = np.array([w.vector for w in self[overlap]])
        mat2 = np.array([w.vector for w in other[overlap]])
        return (
            pd.DataFrame(
                {"name": overlap, "movement": paired_distances(mat1, mat2, metric)}
            )
            .sort_values(["movement"], ascending=False)
            .reset_index()
        )

    def to_axis_df(self, x_axis, y_axis):
        if isinstance(x_axis, str):
            x_axis = self[x_axis]
        if isinstance(y_axis, str):
            y_axis = self[y_axis]
        return pd.DataFrame(
            {
                "x_axis": self.compare_against(x_axis),
                "y_axis": self.compare_against(y_axis),
                "name": [v.name for v in self.embeddings.values()],
                "original": [v.orig for v in self.embeddings.values()],
            }
        )

    def plot(
        self,
        kind: str = "scatter",
        x_axis: str = None,
        y_axis: str = None,
        color: str = None,
        show_ops: str = False,
        **kwargs,
    ):
        """
        Makes (perhaps inferior) matplotlib plot. Consider using `plot_interactive` instead.

        Arguments:
            kind: what kind of plot to make, can be `scatter`, `arrow` or `text`
            x_axis: the x-axis to be used, must be given when dim > 2
            y_axis: the y-axis to be used, must be given when dim > 2
            color: the color of the dots
            show_ops: setting to also show the applied operations, only works for `text`
        """
        for k, token in self.embeddings.items():
            token.plot(
                kind=kind,
                x_axis=x_axis,
                y_axis=y_axis,
                color=color,
                show_ops=show_ops,
                **kwargs,
            )
        return self

    def plot_graph_layout(self, kind="cosine", **kwargs):
        plot_graph_layout(self.embeddings, kind, **kwargs)
        return self

    def plot_correlation(self, metric=None):
        """
        Make a correlation plot. Shows you the correlation between all the word embeddings. Can
        also be configured to show distances instead.

        Arguments:
            metric: don't plot correlation but a distance measure, must be scipy compatible (cosine, euclidean, etc)

        Usage:

        ```python
        from whatlies.language import SpacyLanguage
        lang = SpacyLanguage("en_core_web_md")

        names = ['red', 'blue', 'green', 'yellow', 'cat', 'dog', 'mouse', 'rat', 'bike', 'car']
        emb = lang[names]
        emb.plot_correlation()
        ```

        ![](https://rasahq.github.io/whatlies/images/corrplot.png)
        """
        df = self.to_dataframe().T
        corr_df = (
            pairwise_distances(self.to_matrix(), metric=metric) if metric else df.corr()
        )

        fig, ax = plt.subplots()
        plt.imshow(corr_df)
        plt.xticks(range(len(df.columns)), df.columns)
        plt.yticks(range(len(df.columns)), df.columns)
        plt.colorbar()

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=90, ha="right", rotation_mode="anchor")
        plt.show()

    def plot_pixels(self):
        """
        Makes a pixelchart of every embedding in the set.

        Usage:

        ```python
        from whatlies.language import SpacyLanguage
        lang = SpacyLanguage("en_core_web_md")

        names = ['red', 'blue', 'green', 'yellow',
                 'cat', 'dog', 'mouse', 'rat',
                 'bike', 'car', 'motor', 'cycle',
                 'firehydrant', 'japan', 'germany', 'belgium']
        emb = lang[names].transform(Pca(12)).filter(lambda e: 'pca' not in e.name)
        emb.plot_pixels()
        ```

        ![](https://rasahq.github.io/whatlies/images/pixels.png)
        """
        names = self.embeddings.keys()
        df = self.to_dataframe()
        plt.matshow(df)
        plt.yticks(range(len(names)), names)

    def plot_movement(
        self,
        other,
        x_axis: Union[str, Embedding],
        y_axis: Union[str, Embedding],
        first_group_name="before",
        second_group_name="after",
        annot: bool = True,
    ):
        """
        Makes highly interactive plot of the movement of embeddings
        between two sets of embeddings.

        Arguments:
            other: the other embeddingset
            x_axis: the x-axis to be used, must be given when dim > 2
            y_axis: the y-axis to be used, must be given when dim > 2
            first_group_name: the name to give to the first set of embeddings (default: "before")
            second_group_name: the name to give to the second set of embeddings (default: "after")
            annot: drawn points should be annotated

        **Usage**

        ```python
        from whatlies.language import SpacyLanguage

        words = ["prince", "princess", "nurse", "doctor", "banker", "man", "woman",
                 "cousin", "neice", "king", "queen", "dude", "guy", "gal", "fire",
                 "dog", "cat", "mouse", "red", "bluee", "green", "yellow", "water",
                 "person", "family", "brother", "sister"]

        lang = SpacyLanguage("en_core_web_md")
        emb = lang[words]
        emb_new = emb - emb['king']

        emb.plot_difference(emb_new, 'man', 'woman')
        ```
        """
        if isinstance(x_axis, str):
            x_axis = self[x_axis]
        if isinstance(y_axis, str):
            y_axis = self[y_axis]

        df1 = (
            self.to_axis_df(x_axis, y_axis).set_index("original").drop(columns=["name"])
        )
        df2 = (
            other.to_axis_df(x_axis, y_axis)
            .set_index("original")
            .drop(columns=["name"])
            .loc[lambda d: d.index.isin(df1.index)]
        )
        df_draw = (
            pd.concat([df1, df2])
            .reset_index()
            .sort_values(["original"])
            .assign(constant=1)
        )

        plots = []
        for idx, grp_df in df_draw.groupby("original"):
            _ = (
                alt.Chart(grp_df)
                .mark_line(color="gray", strokeDash=[2, 1])
                .encode(x="x_axis:Q", y="y_axis:Q")
            )
            plots.append(_)
        p0 = reduce(lambda x, y: x + y, plots)

        p1 = (
            deepcopy(self)
            .add_property("group", lambda d: first_group_name)
            .plot_interactive(
                x_axis, y_axis, annot=annot, show_axis_point=True, color="group"
            )
        )
        p2 = (
            deepcopy(other)
            .add_property("group", lambda d: second_group_name)
            .plot_interactive(
                x_axis, y_axis, annot=annot, show_axis_point=True, color="group"
            )
        )
        return p0 + p1 + p2

    def plot_interactive(
        self,
        x_axis: Union[str, Embedding],
        y_axis: Union[str, Embedding],
        annot: bool = True,
        show_axis_point: bool = False,
        color: Union[None, str] = None,
    ):
        """
        Makes highly interactive plot of the set of embeddings.

        Arguments:
            x_axis: the x-axis to be used, must be given when dim > 2
            y_axis: the y-axis to be used, must be given when dim > 2
            annot: drawn points should be annotated
            show_axis_point: ensure that the axis are drawn
            color: a property that will be used for plotting

        **Usage**

        ```python
        from whatlies.language import SpacyLanguage

        words = ["prince", "princess", "nurse", "doctor", "banker", "man", "woman",
                 "cousin", "neice", "king", "queen", "dude", "guy", "gal", "fire",
                 "dog", "cat", "mouse", "red", "bluee", "green", "yellow", "water",
                 "person", "family", "brother", "sister"]

        lang = SpacyLanguage("en_core_web_md")
        emb = lang[words]

        emb.plot_interactive('man', 'woman')
        ```
        """
        if isinstance(x_axis, str):
            x_axis = self[x_axis]
        if isinstance(y_axis, str):
            y_axis = self[y_axis]

        plot_df = pd.DataFrame(
            {
                "x_axis": self.compare_against(x_axis),
                "y_axis": self.compare_against(y_axis),
                "name": [v.name for v in self.embeddings.values()],
                "original": [v.orig for v in self.embeddings.values()],
            }
        )

        if color:
            plot_df[color] = [
                getattr(v, color) if hasattr(v, color) else ""
                for v in self.embeddings.values()
            ]

        if not show_axis_point:
            plot_df = plot_df.loc[lambda d: ~d["name"].isin([x_axis.name, y_axis.name])]

        result = (
            alt.Chart(plot_df)
            .mark_circle(size=60)
            .encode(
                x=alt.X("x_axis", axis=alt.Axis(title=x_axis.name)),
                y=alt.X("y_axis", axis=alt.Axis(title=y_axis.name)),
                tooltip=["name", "original"],
                color=alt.Color(":N", legend=None) if not color else alt.Color(color),
            )
            .properties(title=f"{x_axis.name} vs. {y_axis.name}")
            .interactive()
        )

        if annot:
            text = (
                alt.Chart(plot_df)
                .mark_text(dx=-15, dy=3, color="black")
                .encode(
                    x=alt.X("x_axis", axis=alt.Axis(title=x_axis.name)),
                    y=alt.X("y_axis", axis=alt.Axis(title=y_axis.name)),
                    text="original",
                )
            )
            result = result + text
        return result

    def plot_interactive_matrix(
        self,
        *axes,
        annot: bool = True,
        show_axis_point: bool = False,
        width: int = 200,
        height: int = 200,
    ):
        """
        Makes highly interactive plot of the set of embeddings.

        Arguments:
            axes: the axes that we wish to plot, these should be in the embeddingset
            annot: drawn points should be annotated
            show_axis_point: ensure that the axis are drawn
            width: width of the visual
            height: height of the visual

        **Usage**

        ```python
        from whatlies.language import SpacyLanguage
        from whatlies.transformers import Pca

        words = ["prince", "princess", "nurse", "doctor", "banker", "man", "woman",
                 "cousin", "neice", "king", "queen", "dude", "guy", "gal", "fire",
                 "dog", "cat", "mouse", "red", "bluee", "green", "yellow", "water",
                 "person", "family", "brother", "sister"]

        lang = SpacyLanguage("en_core_web_md")
        emb = lang[words]

        emb.transform(Pca(3)).plot_interactive_matrix('pca_0', 'pca_1', 'pca_2')
        ```
        """
        plot_df = pd.DataFrame({ax: self.compare_against(self[ax]) for ax in axes})
        plot_df["name"] = [v.name for v in self.embeddings.values()]
        plot_df["original"] = [v.orig for v in self.embeddings.values()]

        if not show_axis_point:
            plot_df = plot_df.loc[lambda d: ~d["name"].isin(axes)]

        result = (
            alt.Chart(plot_df)
            .mark_circle()
            .encode(
                x=alt.X(alt.repeat("column"), type="quantitative"),
                y=alt.Y(alt.repeat("row"), type="quantitative"),
                tooltip=["name", "original"],
                text="original",
            )
        )
        if annot:
            text_stuff = result.mark_text(dx=-15, dy=3, color="black").encode(
                x=alt.X(alt.repeat("column"), type="quantitative"),
                y=alt.Y(alt.repeat("row"), type="quantitative"),
                tooltip=["name", "original"],
                text="original",
            )
            result = result + text_stuff

        result = (
            result.properties(width=width, height=height)
            .repeat(row=axes[::-1], column=axes)
            .interactive()
        )

        return result
