package com.example.dreamcountry.web;

import com.example.dreamcountry.model.Country;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface GetDataService {

    @GET("all") //my custom response
    Call<List<Country>> getAllCountries();

    @GET("alpha") //my custom response
    Call<List<Country>> getNearByCountryByName(@Query("codes") String borders );


}