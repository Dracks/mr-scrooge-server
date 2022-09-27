import useAxios, { UseAxiosResult } from "axios-hooks";

import { TagFilterUrl } from "./constants";
import { PostTagFilterResponse } from "./types";

export const usePutTagFilter = (
    tagId: number
): UseAxiosResult<PostTagFilterResponse> => useAxios(
        {
            url: `${TagFilterUrl}${tagId}/`,
            method: "PUT",
        },
        {
            manual: true,
        }
    )
